# step3_prompt_check.py
import os
import streamlit as st
from utils import CacheManager

cache = CacheManager("step2_cache.pkl")  # Each page uses separate cache file

def run_step3():
    st.header("Step 3 - Prompt Verification")

    # Input directory for TXT files
    txt_folder = st.text_input("📂 Enter folder path containing TXT files:", value=cache.get("txt_folder", ""))
    # Input directory for video files
    video_folder = st.text_input("🎬 Enter video files folder path:", value=cache.get("video_folder", ""))

    cache.set("txt_folder", txt_folder)
    cache.set("video_folder", video_folder)

    if not txt_folder:
        st.info("Please enter a TXT folder path to load files.")
        return

    if not os.path.isdir(txt_folder):
        st.error("❌ Invalid TXT folder path, please check.")
        return

    # Get all TXT files in directory
    txt_files = [f for f in os.listdir(txt_folder) if f.lower().endswith(".txt")]
    if not txt_files:
        st.warning("⚠️ No TXT files found in this folder.")
        return

    st.success(f"Found {len(txt_files)} TXT files.")

    # Supported video formats
    video_exts = [".mp4", ".mov", ".avi", ".mkv", ".webm"]

    for filename in txt_files:
        txt_path = os.path.join(txt_folder, filename)

        # Read TXT file content
        try:
            with open(txt_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            st.error(f"Error reading {filename}: {e}")
            continue

        # Find matching video file
        video_path = None
        if video_folder and os.path.isdir(video_folder):
            name_without_ext = os.path.splitext(filename)[0]
            for ext in video_exts:
                candidate = os.path.join(video_folder, name_without_ext + ext)
                if os.path.exists(candidate):
                    video_path = candidate
                    break

        # Layout: Text editor + Video preview
        cols = st.columns([2, 1])  # 2:1 ratio for text vs video

        with cols[0]:
            st.subheader(f"📄 {filename}")
            new_content = st.text_area(
                f"Edit {filename}",
                value=content,
                height=200,
                key=f"text_{filename}"
            )

            if st.button(f"💾 Save {filename}", key=f"save_{filename}"):
                try:
                    with open(txt_path, "w", encoding="utf-8") as f:
                        f.write(new_content)
                    st.success(f"✅ {filename} saved successfully!")
                except Exception as e:
                    st.error(f"❌ Failed to save {filename}: {e}")

        with cols[1]:
            st.subheader("Video Preview")
            if video_path:
                st.write(f"🎬 Found video file: **{os.path.basename(video_path)}**")
                # Toggle video playback
                play = st.button("▶️ Play/Pause", key=f"play_{filename}")
                if play:
                    st.video(video_path)
            else:
                st.info("⚠️ No matching video file found")
