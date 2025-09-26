import os
import random
import shutil
import cv2
import streamlit as st
from collections import defaultdict
from PIL import Image
from scenedetect import VideoManager, SceneManager
from scenedetect.detectors import ContentDetector

# ==== 第一部分：视频镜头抽帧工具 ====
def detect_scenes(video_path, threshold=27.0):
    video_manager = VideoManager([video_path])
    scene_manager = SceneManager()
    scene_manager.add_detector(ContentDetector(threshold=threshold))
    video_manager.set_downscale_factor()
    video_manager.start()
    scene_manager.detect_scenes(frame_source=video_manager)
    scene_list = scene_manager.get_scene_list()
    video_manager.release()
    return scene_list

def extract_frames(video_path, scene_list, temp_dir):
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    cap = cv2.VideoCapture(video_path)
    scene_frames = {}
    for i, (start, end) in enumerate(scene_list, 1):
        start_frame = int(start.get_frames())
        end_frame = int(end.get_frames())
        if end_frame <= start_frame:
            continue
        safe_end_frame = max(start_frame, end_frame - 2)
        middle_frames = []
        if safe_end_frame - start_frame > 2:
            middle_frames = random.sample(
                range(start_frame + 1, safe_end_frame - 1),
                k=min(2, safe_end_frame - start_frame - 1)
            )
        frame_ids = [start_frame, safe_end_frame] + middle_frames
        frame_ids = sorted(set(frame_ids))
        images = []
        for f in frame_ids:
            cap.set(cv2.CAP_PROP_POS_FRAMES, f)
            ret, frame = cap.read()
            if ret:
                img_path = os.path.join(temp_dir, f"scene_{i}_frame_{f}.jpg")
                cv2.imwrite(img_path, frame)
                images.append(img_path)
        scene_frames[i] = images
    cap.release()
    return scene_frames

# ==== 第二部分：人物分组工具 ====
SIM_THRESHOLD = 0.6
IMAGES_PER_ROW = 4

def get_role_label(idx: int) -> str:
    label = ""
    while True:
        idx, rem = divmod(idx, 26)
        label = chr(ord("A") + rem) + label
        if idx == 0:
            break
        idx -= 1
    return label

def group_roles(input_dir, output_dir, det_threshold=0.75, extract_feature=None, cosine_sim=None):
    role_features = {}
    role_images = defaultdict(list)
    next_role_id = 0

    for img_name in os.listdir(input_dir):
        img_path = os.path.join(input_dir, img_name)
        if not img_path.lower().endswith((".jpg", ".png", ".jpeg")):
            continue
        features = extract_feature(img_path, det_threshold=det_threshold)
        if len(features) == 0:
            role_images["other"].append(img_name)
        else:
            for feat in features:
                matched_role = None
                best_sim = 0
                for role, ref_feat in role_features.items():
                    sim = cosine_sim(feat, ref_feat)
                    if sim > best_sim:
                        best_sim = sim
                        matched_role = role
                if matched_role and best_sim >= SIM_THRESHOLD:
                    role_images[matched_role].append(img_name)
                else:
                    new_role = get_role_label(next_role_id)
                    role_features[new_role] = feat
                    role_images[new_role].append(img_name)
                    next_role_id += 1

    os.makedirs(output_dir, exist_ok=True)
    for role, images in role_images.items():
        role_dir = os.path.join(output_dir, f"role_{role}")
        os.makedirs(role_dir, exist_ok=True)
        for img_name in set(images):
            src = os.path.join(input_dir, img_name)
            dst = os.path.join(role_dir, img_name)
            if not os.path.exists(dst):
                shutil.copy(src, dst)
    return role_images

def display_images(images, input_dir, container):
    for i in range(0, len(images), IMAGES_PER_ROW):
        cols = container.columns(IMAGES_PER_ROW)
        for col, img_name in zip(cols, images[i:i + IMAGES_PER_ROW]):
            img_path = os.path.join(input_dir, img_name)
            try:
                img = Image.open(img_path)
                col.image(img, caption=img_name, width="stretch")
            except:
                col.write(f"无法加载 {img_name}")

# ==== Streamlit 主程序 ====
st.title("📽 视频处理与人物分组工具")
st.sidebar.title("导航栏")
app_mode = st.sidebar.radio("选择功能", ["镜头抽帧", "人物分组"])

# ---- 镜头抽帧 ----
if app_mode == "镜头抽帧":
    video_path = st.text_input("输入视频路径", "1.mp4")
    output_dir = st.text_input("输出目录", "output/frames")
    threshold = st.slider("镜头检测阈值", 20.0, 50.0, 35.0)

    if st.button("开始检测并抽帧"):
        if not os.path.exists(video_path):
            st.error("视频文件不存在")
        else:
            scenes = detect_scenes(video_path, threshold)
            st.success(f"检测到 {len(scenes)} 个镜头！")

            temp_dir = os.path.join(output_dir, "temp")
            scene_frames = extract_frames(video_path, scenes, temp_dir)
            st.session_state["scene_frames"] = scene_frames
            st.session_state["temp_dir"] = temp_dir
            st.session_state["output_dir"] = output_dir

    if "scene_frames" in st.session_state:
        selected_images_per_scene = []
        for scene_id, images in st.session_state["scene_frames"].items():
            st.markdown(f"### 镜头 {scene_id}")
            cols = st.columns(len(images))
            for j, img in enumerate(images):
                with cols[j]:
                    st.image(img, width="stretch", caption=os.path.basename(img))
                    checked_default = True if j == 0 else False
                    checked = st.checkbox(
                        f"选择 {os.path.basename(img)}",
                        key=f"scene_{scene_id}_{j}",
                        value=checked_default
                    )
                    if checked:
                        selected_images_per_scene.append((scene_id, img))

        if st.button("保存选择结果"):
            save_dir = os.path.join(st.session_state["output_dir"], "selected")
            os.makedirs(save_dir, exist_ok=True)

            # 按镜头编号+顺序保存
            scene_counter = defaultdict(int)
            for scene_id, img_path in selected_images_per_scene:
                scene_counter[scene_id] += 1
                idx = scene_counter[scene_id]
                if idx == 1:
                    base_name = f"cut({scene_id}).jpg"
                else:
                    base_name = f"cut({scene_id}.{idx}).jpg"
                save_path = os.path.join(save_dir, base_name)
                shutil.copy(img_path, save_path)

            # 删除临时帧
            temp_dir = st.session_state.get("temp_dir")
            if temp_dir and os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)

            st.success(f"保存完成！结果保存在: {save_dir}")
            st.session_state["last_saved_dir"] = save_dir  # 保存路径用于第二步默认输入

# ---- 人物分组 ----
elif app_mode == "人物分组":
    # 默认输入路径为第一步保存路径
    default_input = st.session_state.get("last_saved_dir", "output/frames/selected")
    input_dir = st.text_input("输入目录:", default_input)
    output_dir = st.text_input("输出目录 (默认同输入目录):", input_dir)

    det_threshold = st.slider(
        "人脸检测置信度阈值",
        0.0, 1.0, 0.75, 0.05
    )

    if "role_images" not in st.session_state:
        st.session_state.role_images = {}

    if st.button("开始分组"):
        if not os.path.exists(input_dir):
            st.error("输入目录不存在")
        else:
            from utils.face_utils import extract_feature, cosine_sim
            st.session_state.role_images = group_roles(
                input_dir, output_dir, det_threshold=det_threshold,
                extract_feature=extract_feature, cosine_sim=cosine_sim
            )
            st.success(f"分组完成！（det_threshold={det_threshold}）")

    roles_to_delete = []
    for role, images in st.session_state.role_images.items():
        container = st.container()
        with container:
            col1, col2 = st.columns([8, 1])
            col1.subheader(f"角色 {role} - {len(images)} 张图片")
            role_dir = os.path.join(output_dir, f"role_{role}")
            if col2.button("删除", key=f"delete_{role}"):
                if os.path.exists(role_dir):
                    shutil.rmtree(role_dir)
                roles_to_delete.append(role)
                container.empty()
                continue
            display_images(images, input_dir, container)

    for role in roles_to_delete:
        st.session_state.role_images.pop(role, None)