import os
import random
import shutil
import cv2
import streamlit as st
import numpy as np
from collections import defaultdict
from scenedetect import VideoManager, SceneManager
from scenedetect.detectors import ContentDetector
from sklearn.cluster import KMeans

# ======================================================
# 高级镜头检测函数（带聚类合并）
# ======================================================
def detect_scenes_advanced(video_path, threshold=27.0, mode="smart"):
    """
    mode:
        - "basic" : 仅用 scenedetect (最快)
        - "smart" : 聚类相似镜头合并（推荐）
        - "ai"    : 保留扩展接口（未来可用 CLIP 特征）
    """
    video_manager = VideoManager([video_path])
    scene_manager = SceneManager()
    scene_manager.add_detector(ContentDetector(threshold=threshold))
    video_manager.set_downscale_factor()
    video_manager.start()
    scene_manager.detect_scenes(frame_source=video_manager)
    scenes = scene_manager.get_scene_list()
    video_manager.release()

    if mode == "basic" or len(scenes) <= 2:
        return scenes

    # Step 2: 提取每个镜头中间帧特征
    cap = cv2.VideoCapture(video_path)
    features = []
    for start, end in scenes:
        mid = int((start.get_frames() + end.get_frames()) / 2)
        cap.set(cv2.CAP_PROP_POS_FRAMES, mid)
        ret, frame = cap.read()
        if not ret:
            features.append(np.zeros(64))
            continue
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        hist = cv2.calcHist([hsv], [0, 1], None, [8, 8], [0, 180, 0, 256])
        features.append(cv2.normalize(hist, hist).flatten())
    cap.release()

    # Step 3: KMeans 聚类合并相似镜头
    k = max(2, len(features) // 4)
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=5)
    labels = kmeans.fit_predict(features)

    merged_scenes = []
    current_label = labels[0]
    start = scenes[0][0]
    for i in range(1, len(scenes)):
        if labels[i] != current_label:
            merged_scenes.append((start, scenes[i - 1][1]))
            start = scenes[i][0]
            current_label = labels[i]
    merged_scenes.append((start, scenes[-1][1]))
    return merged_scenes

# ======================================================
# 抽帧
# ======================================================
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
        frame_ids = sorted(set([start_frame, safe_end_frame] + middle_frames))
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

# ======================================================
# 切割视频
# ======================================================
def cut_video_segments(video_path, scene_list, cuts_dir):
    os.makedirs(cuts_dir, exist_ok=True)
    for i, (start, end) in enumerate(scene_list, 1):
        start_time = start.get_seconds()
        end_time = end.get_seconds()
        output_path = os.path.join(cuts_dir, f"cut({i}).mp4")
        cmd = (
            f'ffmpeg -y -i "{video_path}" '
            f'-ss {start_time:.3f} -to {end_time:.3f} '
            f'-c:v libx264 -crf 23 -preset veryfast -c:a copy "{output_path}"'
        )
        os.system(cmd)

# ======================================================
# 清理旧数据
# ======================================================
def clean_previous_run(output_dir):
    for sub in ["selected", "temp", "cuts"]:
        path = os.path.join(output_dir, sub)
        if os.path.exists(path):
            shutil.rmtree(path)
            print(f"已清理旧目录: {path}")

# ======================================================
# 主流程 UI
# ======================================================
def run_step0():
    st.header("Step 1 - 智能镜头抽帧 ✨")

    video_path = st.text_input("输入视频路径", "1.mp4")
    output_dir = st.text_input("输出目录", "output/frames")
    threshold = st.slider("镜头检测阈值", 20.0, 50.0, 35.0)
    mode = st.radio("检测模式", ["basic", "smart"], index=1, horizontal=True)

    if st.button("开始检测并抽帧"):
        if not os.path.exists(video_path):
            st.error("视频文件不存在")
        else:
            clean_previous_run(output_dir)

            st.info("🔍 正在检测镜头，请稍候...")
            scenes = detect_scenes_advanced(video_path, threshold, mode)
            st.success(f"检测到 {len(scenes)} 个镜头！")

            temp_dir = os.path.join(output_dir, "temp")
            scene_frames = extract_frames(video_path, scenes, temp_dir)
            st.session_state.update({
                "scene_frames": scene_frames,
                "temp_dir": temp_dir,
                "output_dir": output_dir,
                "scenes": scenes,
                "video_path": video_path
            })

    if "scene_frames" in st.session_state:
        selected_images = []
        for scene_id, images in st.session_state["scene_frames"].items():
            st.markdown(f"### 镜头 {scene_id}")
            cols = st.columns(len(images))
            for j, img in enumerate(images):
                with cols[j]:
                    st.image(img, caption=os.path.basename(img), use_container_width=True)
                    if st.checkbox(f"选 {os.path.basename(img)}", key=f"scene_{scene_id}_{j}", value=(j == 0)):
                        selected_images.append((scene_id, img))

        if st.button("保存选择结果并切割视频"):
            base_dir = st.session_state["output_dir"]
            save_dir = os.path.join(base_dir, "selected")
            cuts_dir = os.path.join(base_dir, "cuts")
            os.makedirs(save_dir, exist_ok=True)

            scene_counter = defaultdict(int)
            for scene_id, img_path in selected_images:
                scene_counter[scene_id] += 1
                idx = scene_counter[scene_id]
                name = f"cut({scene_id}).jpg" if idx == 1 else f"cut({scene_id}.{idx}).jpg"
                shutil.copy(img_path, os.path.join(save_dir, name))

            cut_video_segments(st.session_state["video_path"], st.session_state["scenes"], cuts_dir)
            st.success(f"✅ 保存完成！\n图片: {save_dir}\n视频: {cuts_dir}")