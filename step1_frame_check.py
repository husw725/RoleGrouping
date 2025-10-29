import os
import cv2
import streamlit as st
from pathlib import Path
import pickle

from utils import CacheManager

cache = CacheManager("step1_cache.pkl")  # 每个页面可以使用不同的文件名

# ----------------- 抽取四帧 -----------------
def extract_frames(video_path, num_frames=4):
    cap = cv2.VideoCapture(video_path)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if frame_count < num_frames:
        indices = list(range(frame_count))
    else:
        indices = [0, frame_count // 3, (frame_count * 2) // 3, frame_count - 1]
    frames = []
    for idx in indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ret, frame = cap.read()
        if ret:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frames.append((idx, frame_rgb))
    cap.release()
    return frames

# ----------------- 主函数 -----------------
def run_step1():
    st.title("Step 1 - Key Frame Selection")

    # 读取上次目
    input_dir = st.text_input("Input Directory", value=cache.get("input_dir", ""))
    output_dir = st.text_input("Output Directory", value=cache.get("output_dir", ""))

    cache.set("input_dir", input_dir)
    cache.set("output_dir", output_dir)

    if not input_dir or not output_dir:
        st.warning("Please set input and output directories")
        return  

    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    video_files = list(input_path.glob("*.mp4")) + list(input_path.glob("*.mov"))
    if not video_files:
        st.info("Input directory does not contain any video files")
        return     
    st.write(f"Found {len(video_files)} video files")

    # 保存选中的帧
    selected_frames = {}

    for video_file in video_files:
        st.subheader(video_file.name)
        frames = extract_frames(str(video_file))
        cols = st.columns(len(frames))
        checkboxes = []
        for i, (frame_idx, frame_img) in enumerate(frames):
            with cols[i]:
                st.image(frame_img, width='stretch')
                default_checked = True if i == 0 else False
                checked = st.checkbox(f"Select", key=f"{video_file.name}_{i}", value=default_checked)
                checkboxes.append((frame_idx, frame_img, checked))
        selected_frames[video_file] = checkboxes
 
    if st.button("Save Selected Frames"):
        for video_file, frame_list in selected_frames.items():
            base_name = video_file.stem
            count = 0  # 用于顺序编号
            for i, (frame_idx, frame_img, checked) in enumerate(frame_list):
                if checked:
                    count += 1
                    if count == 1:
                        filename = f"{base_name}.jpg"
                    else:
                        filename = f"{base_name}.{count}.jpg"
                    save_path = output_path / filename
                    cv2.imwrite(str(save_path), cv2.cvtColor(frame_img, cv2.COLOR_RGB2BGR))
        st.success("Selected frames saved!")