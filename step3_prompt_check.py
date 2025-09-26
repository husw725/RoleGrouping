# step3_prompt_check.py
import os
import streamlit as st

def run_step3():
    st.header("Step 3 - 提示词查验")

    # 输入文件夹路径
    folder_path = st.text_input("请输入包含 txt 文件的文件夹路径:")

    if not folder_path:
        st.info("请输入文件夹路径以加载文件内容。")
        return

    if not os.path.isdir(folder_path):
        st.error("❌ 输入的路径不存在或不是文件夹，请检查。")
        return

    # 获取该目录下所有txt文件
    txt_files = [f for f in os.listdir(folder_path) if f.endswith(".txt")]

    if not txt_files:
        st.warning("⚠️ 该文件夹下没有找到 txt 文件。")
        return

    st.success(f"共找到 {len(txt_files)} 个 txt 文件。")

    # 逐个显示文件内容
    for filename in txt_files:
        file_path = os.path.join(folder_path, filename)

        # 读取文件内容
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            st.error(f"读取文件 {filename} 出错: {e}")
            continue

        st.subheader(f"📄 {filename}")
        new_content = st.text_area(
            f"编辑 {filename}",
            value=content,
            height=200,
            key=f"text_{filename}"
        )

        # 保存按钮
        if st.button(f"💾 保存 {filename}", key=f"save_{filename}"):
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(new_content)
                st.success(f"✅ {filename} 已保存成功！")
            except Exception as e:
                st.error(f"❌ 保存 {filename} 失败: {e}")