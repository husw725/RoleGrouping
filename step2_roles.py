import os
import shutil
import numpy as np
import streamlit as st
from collections import defaultdict
from utils.face_utils import extract_feature, cosine_sim
from utils.ui_utils import display_images
from utils.file_utils import get_role_label
import cv2

DET_THRESHOLD = 0.65
IMAGES_PER_ROW = 4

from utils import CacheManager
cache = CacheManager("step2_cache.pkl")


# -----------------------------
# 工具函数
# -----------------------------
def normalize(v):
    return v / (np.linalg.norm(v) + 1e-6)


def compute_clarity(img_path):
    """返回 0~1 之间清晰度分数"""
    img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        return 0.3

    lap = cv2.Laplacian(img, cv2.CV_64F)
    score = lap.var()

    # normalize
    score = min(score / 1500.0, 1.0)
    return max(score, 0.05)


# -----------------------------
# 第一阶段：快速聚类
# -----------------------------
def first_pass_clustering(file_list, input_dir, sim_threshold):
    role_centroids = {}
    role_feature_list = defaultdict(list)
    role_images = defaultdict(set)
    next_role_id = 0

    # 缓存特征，减少重复计算
    feature_cache = {}

    for img_name in file_list:
        img_path = os.path.join(input_dir, img_name)

        # 缓存机制：提高 3-10 倍速度
        if img_name not in feature_cache:
            features = extract_feature(img_path, det_threshold=DET_THRESHOLD)
            feature_cache[img_name] = features
        else:
            features = feature_cache[img_name]

        if not features:
            role_images["other"].add(img_name)
            continue

        clarity = compute_clarity(img_path)

        for feat in features:
            feat = normalize(np.array(feat))

            matched_role = None
            best_sim = -1

            # 与已有角色比较
            for role, centroid in role_centroids.items():
                sim = cosine_sim(feat, centroid)
                if sim > best_sim:
                    best_sim = sim
                    matched_role = role

            # 自适应阈值（清晰度越低，阈值越低）
            adaptive_thr = sim_threshold * (0.8 + clarity * 0.2)

            if best_sim < adaptive_thr:
                new_role = get_role_label(next_role_id)
                next_role_id += 1

                role_feature_list[new_role].append((feat, clarity))
                role_centroids[new_role] = feat
                role_images[new_role].add(img_name)
                continue

            # 匹配
            role_feature_list[matched_role].append((feat, clarity))

            feats = np.array([f for f, w in role_feature_list[matched_role]])
            weights = np.array([w**2 for f, w in role_feature_list[matched_role]])  # gamma 加权

            weighted_centroid = np.average(feats, axis=0, weights=weights)
            weighted_centroid = normalize(weighted_centroid)
            role_centroids[matched_role] = weighted_centroid

            role_images[matched_role].add(img_name)

    return role_centroids, feature_cache


# -----------------------------
# 第二阶段：refine 聚类（提升准确度）
# -----------------------------
def second_pass_assign(
        file_list, input_dir, role_centroids, feature_cache, sim_threshold):

    final_groups = defaultdict(set)

    for img_name in file_list:
        img_path = os.path.join(input_dir, img_name)

        features = feature_cache.get(img_name)
        if not features:
            final_groups["other"].add(img_name)
            continue

        clarity = compute_clarity(img_path)

        for feat in features:
            feat = normalize(np.array(feat))

            matched_role = None
            best_sim = -1

            for role, centroid in role_centroids.items():
                sim = cosine_sim(feat, centroid)
                if sim > best_sim:
                    best_sim = sim
                    matched_role = role

            adaptive_thr = sim_threshold * (0.8 + clarity * 0.2)

            if best_sim >= adaptive_thr:
                final_groups[matched_role].add(img_name)
            else:
                final_groups["other"].add(img_name)

    return final_groups


# -----------------------------
# 主函数：两阶段聚类
# -----------------------------
def group_roles(input_dir, output_dir, sim_threshold=0.55):
    os.makedirs(output_dir, exist_ok=True)

    file_list = [
        f for f in os.listdir(input_dir)
        if f.lower().endswith((".jpg", ".jpeg", ".png"))
    ]

    # ---- 第一阶段: 建立初步角色 centroid ----
    centroids, feature_cache = first_pass_clustering(
        file_list, input_dir, sim_threshold
    )

    # ---- 第二阶段: refine 聚类（准确度更高）----
    final_groups = second_pass_assign(
        file_list, input_dir, centroids, feature_cache, sim_threshold
    )

    # 输出
    for role, images in final_groups.items():
        role_dir = os.path.join(output_dir, f"role_{role}")
        os.makedirs(role_dir, exist_ok=True)

        for img_name in images:
            src = os.path.join(input_dir, img_name)
            dst = os.path.join(role_dir, img_name)
            if not os.path.exists(dst):
                shutil.copy(src, dst)

    return {k: list(v) for k, v in final_groups.items()}


# ------------------------------------------------
# Streamlit 页面逻辑（无需修改）
# ------------------------------------------------
def run_step2():
    st.header("Step 2 - Character Grouping")

    input_dir = st.text_input("Input Directory:", cache.get("input_dir", ""))
    output_dir = st.text_input("Output Directory:", cache.get("output_dir", ""))

    cache.set("input_dir", input_dir)
    cache.set("output_dir", output_dir)

    sim_threshold = st.slider("Sim Threshold", 0.0, 1.0, 0.55, 0.05)

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