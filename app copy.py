import os
from collections import defaultdict
from face_utils import extract_feature, cosine_sim

IMAGE_DIR = "inputs"
SIM_THRESHOLD = 0.6

def get_role_label(idx: int) -> str:
    """Convert index to role label: 0->A, 1->B, ..., 25->Z, 26->AA, etc."""
    label = ""
    while True:
        idx, rem = divmod(idx, 26)
        label = chr(ord("A") + rem) + label
        if idx == 0:
            break
        idx -= 1
    return label

def main():
    role_features = {}  # {role_label: feature_vector}
    role_images = defaultdict(list)  # {role_label: [image_names]}

    next_role_id = 0

    for img_name in os.listdir(IMAGE_DIR):
        img_path = os.path.join(IMAGE_DIR, img_name)
        if not img_path.lower().endswith((".jpg", ".png", ".jpeg")):
            continue

        # 提取特征（每个人一个向量）
        features = extract_feature(img_path)
        if len(features) == 0:
            role_images["other"].append(img_name)
        else:
            for feat in features:
                matched_role = None
                best_sim = 0

                # 与已知角色比对
                for role, ref_feat in role_features.items():
                    sim = cosine_sim(feat, ref_feat)
                    if sim > best_sim:
                        best_sim = sim
                        matched_role = role
                print(f"图片 {img_name} 与 {matched_role} 的相似度为 {best_sim:.2f}")
                # 如果相似度超过阈值 -> 归到已有角色
                if matched_role and best_sim >= SIM_THRESHOLD:
                    role_images[matched_role].append(img_name)
                else:
                    # 新角色
                    new_role = get_role_label(next_role_id)
                    role_features[new_role] = feat
                    role_images[new_role].append(img_name)
                    next_role_id += 1

    # 输出结果
    for role, images in role_images.items():
        print(f"角色 {role}: 出现于 {sorted(set(images))}")

if __name__ == "__main__":
    main()