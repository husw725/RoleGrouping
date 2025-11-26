# step3_prompt_check.py
import os
import re
import streamlit as st
from utils import CacheManager

cache = CacheManager("step2_cache.pkl")  # Each page uses separate cache file

def natural_sort_key(s):
    """Sort strings with numbers in a natural order."""
    return [int(text) if text.isdigit() else text.lower() for text in re.split('([0-9]+)', s)]

def run_step3():
    st.header("Step 3 - Prompt Verification")

    # --- Input Fields ---
    with st.container():
        txt_folder = st.text_input(
            "📂 Enter folder path for TXT/SRT files:", 
            value=cache.get("txt_folder", "")
        )
        video_folder = st.text_input(
            "🎬 Enter folder path for video files:", 
            value=cache.get("video_folder", "")
        )
        cache.set("txt_folder", txt_folder)
        cache.set("video_folder", video_folder)

    if not txt_folder or not os.path.isdir(txt_folder):
        st.info("Please enter a valid folder path for TXT/SRT files to begin.")
        return

    # --- File Discovery and Display ---
    try:
        text_files = [f for f in os.listdir(txt_folder) if f.lower().endswith((".txt", ".srt"))]
        if not text_files:
            st.warning("⚠️ No TXT or SRT files found in the specified folder.")
            return
        
        text_files.sort(key=natural_sort_key)
        
        st.success(f"Found {len(text_files)} files.")
        
    except Exception as e:
        st.error(f"❌ An error occurred while reading the folder: {e}")
        return

    # --- Display All Files ---
    video_exts = [".mp4", ".mov", ".avi", ".mkv", ".webm"]
    
    for filename in text_files:
        st.markdown("---")
        txt_path = os.path.join(txt_folder, filename)
        
        # Read file content
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
        cols = st.columns([3, 2])  # 3:2 ratio for text vs video

        with cols[0]:
            st.subheader(f"📄 Editor: `{filename}`")
            new_content = st.text_area(
                "File content:",
                value=content,
                height=300,
                key=f"text_{filename}"
            )

            if st.button(f"💾 Save Changes", key=f"save_{filename}"):
                try:
                    with open(txt_path, "w", encoding="utf-8") as f:
                        f.write(new_content)
                    st.success(f"✅ `{filename}` saved successfully!")
                except Exception as e:
                    st.error(f"❌ Failed to save `{filename}`: {e}")

        with cols[1]:
            st.subheader("🎬 Video Preview")
            if video_path:
                st.video(video_path)
                st.caption(f"Playing: `{os.path.basename(video_path)}`")
            else:
                st.info("ⓘ No matching video file found for this text file.")
