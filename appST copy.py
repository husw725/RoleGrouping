import shutil
from collections import defaultdict
import streamlit as st
from PIL import Image
import os

from face_utils import extract_feature, cosine_sim

SIM_THRESHOLD = 0.6
IMAGES_PER_ROW = 4  # 每行显示几张图片，可以调小一点


def get_role_label(idx: int) -> str:
    label = ""
    while True:
        idx, rem = divmod(idx, 26)
        label = chr(ord("A") + rem) + label
        if idx == 0:
            break
        idx -= 1
    return label


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

    # 输出目录
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


def display_images(images, input_dir, container):
    """在 Streamlit 页面展示图片"""
    for i in range(0, len(images), IMAGES_PER_ROW):
        cols = container.columns(IMAGES_PER_ROW)
        for col, img_name in zip(cols, images[i:i + IMAGES_PER_ROW]):
            img_path = os.path.join(input_dir, img_name)
            try:
                img = Image.open(img_path)
                col.image(img, caption=img_name, use_container_width=True)
            except:
                col.write(f"无法加载 {img_name}")


def main():
    st.title("人物分组工具")

    input_dir = st.text_input("输入目录:", "inputs")
    output_dir = st.text_input("输出目录 (默认同输入目录):", input_dir)

    det_threshold = st.slider(
        "人脸检测置信度阈值 (当发现应该进other的没进时可以调高)",
        0.0, 1.0, 0.75, 0.05
    )

    if "role_images" not in st.session_state:
        st.session_state.role_images = {}

    if st.button("开始分组"):
        if not os.path.exists(input_dir):
            st.error("输入目录不存在")
            return

        st.session_state.role_images = group_roles(input_dir, output_dir, det_threshold=det_threshold)
        st.success(f"分组完成！（使用 det_threshold={det_threshold}）")

    roles_to_delete = []

    # 遍历 session_state 中的角色
    for role, images in st.session_state.role_images.items():
        # 每个分类用单独容器管理
        container = st.container()
        with container:
            # 标题 + 删除按钮在同一行
            col1, col2 = st.columns([8, 1])
            col1.subheader(f"角色 {role} - {len(images)} 张图片")
            role_dir = os.path.join(output_dir, f"role_{role}")
            if col2.button("删除", key=f"delete_{role}"):
                # 删除文件夹
                if os.path.exists(role_dir):
                    shutil.rmtree(role_dir)
                # 标记删除
                roles_to_delete.append(role)
                # 清空整个容器，包括标题、按钮和图片
                container.empty()
                continue

            # 显示图片
            display_images(images, input_dir, container)

    # 删除 session_state 中被删除的角色
    for role in roles_to_delete:
        st.session_state.role_images.pop(role, None)


if __name__ == "__main__":
    main()