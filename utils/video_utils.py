import os
import hashlib
import cv2
import shutil
import subprocess
import shlex
from scenedetect import VideoManager, SceneManager
from scenedetect.detectors import ContentDetector

# ---------------- 工具函数 ----------------
def file_md5(path):
    with open(path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()

def get_video_cache_dir(video_path, base_dir="output/frames"):
    video_hash = file_md5(video_path)
    folder_name = f"{os.path.basename(video_path)}_{video_hash}"
    cache_dir = os.path.join(base_dir, "temp_frames", folder_name)
    os.makedirs(cache_dir, exist_ok=True)
    return cache_dir

def cache_video_frames(video_path, cache_dir):
    if any(os.scandir(cache_dir)):
        return
    cap = cv2.VideoCapture(video_path)
    idx = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame_path = os.path.join(cache_dir, f"frame_{idx:06d}.jpg")
        cv2.imwrite(frame_path, frame)
        idx += 1
    cap.release()

def load_frame_from_cache(cache_dir, frame_idx):
    path = os.path.join(cache_dir, f"frame_{frame_idx:06d}.jpg")
    return path if os.path.exists(path) else None

# ---------------- 分镜检测 ----------------
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

def init_scene_boundaries(scene_list, total_frames=None):
    boundaries = {}
    if not scene_list and total_frames:
        boundaries[1] = {"start_frame": 0, "end_frame": total_frames-1}
        return boundaries
    for i, (start, end) in enumerate(scene_list, 1):
        boundaries[i] = {
            "start_frame": int(start.get_frames()),
            "end_frame": int(end.get_frames()) - 1
        }
    return boundaries

# ---------------- 抽帧 ----------------
def extract_frames(scene_boundaries, cache_dir, middle_count=2):
    scene_frames = {}
    for scene_id, bounds in scene_boundaries.items():
        start_frame = bounds["start_frame"]
        end_frame = bounds["end_frame"]

        middle_frames = []
        frame_range = end_frame - start_frame - 1
        if frame_range > 0 and middle_count > 0:
            step = frame_range / (middle_count + 1)
            for i in range(1, middle_count + 1):
                idx = start_frame + round(step * i)
                middle_frames.append(load_frame_from_cache(cache_dir, idx))

        scene_frames[scene_id] = {
            "start": load_frame_from_cache(cache_dir, start_frame),
            "middle": middle_frames,
            "end": load_frame_from_cache(cache_dir, end_frame)
        }
    return scene_frames

# ---------------- 首尾帧微调 ----------------
def shift_frame(current_img, direction, scene_id, scene_boundaries, scene_frames, cache_dir, position):
    frame_idx = int(os.path.basename(current_img).split("_")[-1].split(".")[0])
    new_idx = max(0, frame_idx + direction)
    scene_boundaries[scene_id][f"{position}_frame"] = new_idx
    scene_frames[scene_id][position] = load_frame_from_cache(cache_dir, new_idx)

# ---------------- 视频切割 ----------------
def cut_video_segments(video_path, scene_boundaries, cuts_dir, fps):
    os.makedirs(cuts_dir, exist_ok=True)
    for scene_id, bounds in scene_boundaries.items():
        start_time = bounds["start_frame"] / fps
        end_time = bounds["end_frame"] / fps
        if end_time - start_time <= 0.05:
            continue
        output_path = os.path.join(cuts_dir, f"cut({scene_id}).mp4")
        cmd = f'ffmpeg -y -i {shlex.quote(video_path)} -ss {start_time:.3f} -to {end_time:.3f} -c:v libx264 -crf 23 -preset veryfast -c:a copy -avoid_negative_ts 1 {shlex.quote(output_path)}'
        subprocess.run(cmd, shell=True)