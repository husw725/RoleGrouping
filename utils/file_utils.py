import os
import shutil

def rename_and_copy_images(input_dir, output_dir):
    """整理镜头图片并按 cut(镜头.第几张) 命名"""
    scene_id = 1
    for root, _, files in os.walk(input_dir):
        files = sorted([f for f in files if f.lower().endswith((".jpg", ".png", ".jpeg"))])
        if not files:
            continue

        for idx, f in enumerate(files, 1):
            src = os.path.join(root, f)
            if len(files) == 1:
                new_name = f"cut({scene_id}).jpg"
            else:
                new_name = f"cut({scene_id}.{idx}).jpg"
            dst = os.path.join(output_dir, new_name)
            shutil.copy(src, dst)
        scene_id += 1

def get_role_label(idx: int) -> str:
    label = ""
    while True:
        idx, rem = divmod(idx, 26)
        label = chr(ord("A") + rem) + label
        if idx == 0:
            break
        idx -= 1
    return label