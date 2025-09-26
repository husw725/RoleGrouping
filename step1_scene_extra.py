import os
import random
import shutil
import cv2
import streamlit as st
from collections import defaultdict
from scenedetect import VideoManager, SceneManager
from scenedetect.detectors import ContentDetector

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

def cut_video_segments(video_path, scene_list, cuts_dir):
    """根据 scene_list 切割视频并保存到 cuts_dir 目录"""
    os.makedirs(cuts_dir, exist_ok=True)

    for i, (start, end) in enumerate(scene_list, 1):
        start_time = start.get_seconds()
        end_time = end.get_seconds()
        output_path = os.path.join(cuts_dir, f"cut({i}).mp4")

        # 使用 ffmpeg 快速切割（要求本机已安装 ffmpeg）
        cmd = (
            f'ffmpeg -y -i "{video_path}" '
            f'-ss {start_time:.3f} -to {end_time:.3f} '
            f'-c:v libx264 -crf 23 -preset veryfast -c:a copy "{output_path}"'
        )

        os.system(cmd)

def clean_previous_run(output_dir):
    """
    在新执行前清理上一次的 selected 和 temp 目录
    """
    selected_dir = os.path.join(output_dir, "selected")
    temp_dir = os.path.join(output_dir, "temp")

    for folder in [selected_dir, temp_dir]:
        if os.path.exists(folder):
            shutil.rmtree(folder)
            print(f"已清理旧目录: {folder}")

def run_step1():
    st.header("Step 1 - 镜头抽帧")

    video_path = st.text_input("输入视频路径", "1.mp4")
    output_dir = st.text_input("输出目录", "output/frames")
    threshold = st.slider("镜头检测阈值", 20.0, 50.0, 35.0)

    if st.button("开始检测并抽帧"):
        if not os.path.exists(video_path):
            st.error("视频文件不存在")
        else:
            # 在执行前先清理上一次数据
            clean_previous_run(output_dir)

            scenes = detect_scenes(video_path, threshold)
            st.success(f"检测到 {len(scenes)} 个镜头！")

            temp_dir = os.path.join(output_dir, "temp")
            scene_frames = extract_frames(video_path, scenes, temp_dir)
            st.session_state["scene_frames"] = scene_frames
            st.session_state["temp_dir"] = temp_dir
            st.session_state["output_dir"] = output_dir
            st.session_state["scenes"] = scenes
            st.session_state["video_path"] = video_path

    if "scene_frames" in st.session_state:
        selected_images_per_scene = []
        for scene_id, images in st.session_state["scene_frames"].items():
            st.markdown(f"### 镜头 {scene_id}")
            cols = st.columns(len(images))
            for j, img in enumerate(images):
                with cols[j]:
                    st.image(img, caption=os.path.basename(img), use_container_width=True)
                    checked_default = True if j == 0 else False
                    checked = st.checkbox(
                        f"选择 {os.path.basename(img)}",
                        key=f"scene_{scene_id}_{j}",
                        value=checked_default
                    )
                    if checked:
                        selected_images_per_scene.append((scene_id, img))

        if st.button("保存选择结果并切割视频"):
            base_dir = st.session_state["output_dir"]
            save_dir = os.path.join(base_dir, "selected")
            cuts_dir = os.path.join(base_dir, "cuts")  # 视频保存到 cuts 子目录
            os.makedirs(save_dir, exist_ok=True)

            # 保存选帧 cut({scene_id}).jpg
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

            # 切割视频
            cut_video_segments(
                st.session_state["video_path"],
                st.session_state["scenes"],
                cuts_dir
            )

            st.success(f"保存完成！\n图片在: {save_dir}\n视频在: {cuts_dir}")
            st.session_state["last_saved_dir"] = save_dir
