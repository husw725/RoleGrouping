import os
import shutil
import streamlit as st
from collections import defaultdict
from utils.face_utils import extract_feature, cosine_sim
from utils.ui_utils import display_images
from utils.file_utils import get_role_label

SIM_THRESHOLD = 0.6
IMAGES_PER_ROW = 4

def group_roles(input_dir, output_dir, det_threshold=0.75):
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

def run_step2():
    st.header("Step 2 - 人物分组")

    default_input = st.session_state.get("last_saved_dir", "output/frames/selected")
    input_dir = st.text_input("输入目录:", default_input)
    output_dir = st.text_input("输出目录:", "step2_outputs")

    det_threshold = st.slider("人脸检测阈值", 0.0, 1.0, 0.75, 0.05)

    if "role_images" not in st.session_state:
        st.session_state.role_images = {}

    if st.button("开始分组"):
        if not os.path.exists(input_dir):
            st.error("输入目录不存在")
        else:
            st.session_state.role_images = group_roles(input_dir, output_dir, det_threshold)
            st.success("分组完成！")

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
            display_images(images, input_dir, container, IMAGES_PER_ROW)

    for role in roles_to_delete:
        st.session_state.role_images.pop(role, None)