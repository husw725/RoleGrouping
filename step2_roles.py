import os
import shutil
import numpy as np
import streamlit as st
from collections import defaultdict
from utils.face_utils import extract_feature, cosine_sim
from utils.ui_utils import display_images
from utils.file_utils import get_role_label

# SIM_THRESHOLD = 0.6
DET_THRESHOLD = 0.65
IMAGES_PER_ROW = 4

from utils import CacheManager

cache = CacheManager("step2_cache.pkl")  # Each page uses separate cache file

def normalize(v):
    return v / (np.linalg.norm(v) + 1e-6)


def group_roles(input_dir, output_dir, sim_threshold=0.55):
    # SIM_THRESHOLD = det_threshold 
    role_centroids = {}                      # 每个角色当前中心向量
    role_feature_list = defaultdict(list)    # 多样本特征缓存
    role_images = defaultdict(set)           # 用 set 防止重复添加
    next_role_id = 0

    os.makedirs(output_dir, exist_ok=True)

    file_list = [
        f for f in os.listdir(input_dir)
        if f.lower().endswith((".jpg", ".jpeg", ".png"))
    ]

    for img_name in file_list:
        img_path = os.path.join(input_dir, img_name)

        features = extract_feature(img_path, det_threshold=DET_THRESHOLD)

        if not features:
            role_images["other"].add(img_name)
            continue

        for feat in features:
            feat = normalize(np.array(feat))

            matched_role = None
            best_sim = -1

            # 与所有角色中心比较
            for role, centroid in role_centroids.items():
                sim = cosine_sim(feat, centroid)
                if sim > best_sim:
                    best_sim = sim
                    matched_role = role

            # 阈值外 → 新建角色
            if matched_role is None or best_sim < sim_threshold:
                new_role = get_role_label(next_role_id)
                next_role_id += 1

                role_feature_list[new_role].append(feat)
                role_centroids[new_role] = feat
                role_images[new_role].add(img_name)
                continue

            # 匹配到角色 → 更新特征中心
            role_feature_list[matched_role].append(feat)

            new_centroid = np.mean(role_feature_list[matched_role], axis=0)
            new_centroid = normalize(new_centroid)
            role_centroids[matched_role] = new_centroid

            role_images[matched_role].add(img_name)

    # 保存图片（保证与你原逻辑一致）
    for role, images in role_images.items():
        role_dir = os.path.join(output_dir, f"role_{role}")
        os.makedirs(role_dir, exist_ok=True)
        for img_name in images:
            src = os.path.join(input_dir, img_name)
            dst = os.path.join(role_dir, img_name)
            if not os.path.exists(dst):
                shutil.copy(src, dst)

    return {k: list(v) for k, v in role_images.items()}

def run_step2():
    st.header("Step 2 - Character Grouping")
    
    input_dir = st.text_input("Input Directory:", cache.get("input_dir", ""))
    output_dir = st.text_input("Output Directory:", cache.get("output_dir", ""))

    cache.set("input_dir", input_dir)
    cache.set("output_dir", output_dir)

    sim_threshold = st.slider("Face Detection Threshold", 0.0, 1.0, 0.55, 0.05)

    if "role_images" not in st.session_state:
        st.session_state.role_images = {}

    if st.button("Start Grouping"):
        if not os.path.exists(input_dir):
            st.error("Input directory does not exist")
        else:
            st.session_state.role_images = group_roles(input_dir, output_dir, sim_threshold)
            st.success("Grouping completed!")

    roles_to_delete = []
    for role, images in st.session_state.role_images.items():
        container = st.container()
        with container:
            col1, col2 = st.columns([8, 1])
            col1.subheader(f"Character {role} - {len(images)} images")
            role_dir = os.path.join(output_dir, f"role_{role}")
            if col2.button("Delete", key=f"delete_{role}"):
                if os.path.exists(role_dir):
                    shutil.rmtree(role_dir)
                roles_to_delete.append(role)
                container.empty()
                continue
            display_images(images, input_dir, container, IMAGES_PER_ROW)

    for role in roles_to_delete:
        st.session_state.role_images.pop(role, None)
