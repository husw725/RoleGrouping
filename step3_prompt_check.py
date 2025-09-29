# step3_prompt_check.py
import os
import streamlit as st


from utils import CacheManager

cache = CacheManager("step2_cache.pkl")  # 每个页面可以使用不同的文件名

def run_step3():
    st.header("Step 3 - 提示词查验")

    # 输入 txt 文件目录
    txt_folder = st.text_input("📂 请输入包含 txt 文件的文件夹路径:", value=cache.get("txt_folder", ""))
    # 输入视频文件目录
    video_folder = st.text_input("🎬 请输入视频文件所在文件夹路径:", value=cache.get("video_folder", ""))

    cache.set("txt_folder", txt_folder)
    cache.set("video_folder", video_folder)

    if not txt_folder:
        st.info("请输入 txt 文件夹路径以加载文件内容。")
        return

    if not os.path.isdir(txt_folder):
        st.error("❌ 输入的 txt 路径不存在或不是文件夹，请检查。")
        return

    # 获取该目录下所有 txt 文件
    txt_files = [f for f in os.listdir(txt_folder) if f.lower().endswith(".txt")]
    if not txt_files:
        st.warning("⚠️ 该文件夹下没有找到 txt 文件。")
        return

    st.success(f"共找到 {len(txt_files)} 个 txt 文件。")

    # 支持的视频格式
    video_exts = [".mp4", ".mov", ".avi", ".mkv", ".webm"]

    for filename in txt_files:
        txt_path = os.path.join(txt_folder, filename)

        # 读取 txt 文件内容
        try:
            with open(txt_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            st.error(f"读取文件 {filename} 出错: {e}")
            continue

        # 查找同名视频文件
        video_path = None
        if video_folder and os.path.isdir(video_folder):
            name_without_ext = os.path.splitext(filename)[0]
            for ext in video_exts:
                candidate = os.path.join(video_folder, name_without_ext + ext)
                if os.path.exists(candidate):
                    video_path = candidate
                    break

        # 布局：文本编辑 + 视频
        cols = st.columns([2, 1])  # 左侧 2/3 显示文本，右侧 1/3 显示视频

        with cols[0]:
            st.subheader(f"📄 {filename}")
            new_content = st.text_area(
                f"编辑 {filename}",
                value=content,
                height=200,
                key=f"text_{filename}"
            )

            if st.button(f"💾 保存 {filename}", key=f"save_{filename}"):
                try:
                    with open(txt_path, "w", encoding="utf-8") as f:
                        f.write(new_content)
                    st.success(f"✅ {filename} 已保存成功！")
                except Exception as e:
                    st.error(f"❌ 保存 {filename} 失败: {e}")

        with cols[1]:
            st.subheader("视频预览")
            if video_path:
                st.write(f"🎬 已找到视频文件：**{os.path.basename(video_path)}**")
                # 点击按钮切换播放
                play = st.button("▶️ 播放/暂停", key=f"play_{filename}")
                if play:
                    st.video(video_path)
            else:
                st.info("⚠️ 未找到同名视频文件")
