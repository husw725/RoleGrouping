import streamlit as st
from step1_frame_check import run_step1
from step2_roles import run_step2
from step3_prompt_check import run_step3

def main():
    # 页面配置
    st.set_page_config(
        page_title="人物分组工具",
        layout="wide",
        page_icon="🧩",
        initial_sidebar_state="expanded"
    )

    # 页面标题
    # st.markdown(
    #     """
    #     <h1 style='text-align: center; color: #4B8BBE;'>
    #         🧩 人物分组工具
    #     </h1>
    #     <hr style='height:2px;border:none;color:#4B8BBE;background-color:#4B8BBE;'/>
    #     """,
    #     unsafe_allow_html=True
    # )

    # 侧边栏美化
    st.sidebar.markdown(
        "<h2 style='color:#4B8BBE;'>📌 导航</h2>", 
        unsafe_allow_html=True
    )

    step = st.sidebar.radio(
        "选择步骤",
        ["Step 1 - 关键帧选取", "Step 2 - 人物分组", "Step 3 - 提示词查验"],
        index=0,
        key="step_radio",
        label_visibility="visible"
    )

    # 提示信息
    # st.sidebar.info("💡 请按顺序完成每一步，点击后内容将自动展示在主页面。")

    # 步骤内容显示
    if step == "Step 1 - 关键帧选取":
        # st.markdown("### Step 1 - 关键帧选取")
        run_step1()
    elif step == "Step 2 - 人物分组":
        # st.markdown("### Step 2 - 人物分组")
        run_step2()
    elif step == "Step 3 - 提示词查验":
        # st.markdown("### Step 3 - 提示词查验")
        run_step3()

    # 页脚美化
    st.markdown(
        """
        <hr style='height:1px;border:none;color:#ddd;background-color:#ddd;'/>
        <p style='text-align:center;color:#999;font-size:12px;'>
            &copy; 2025 人物分组工具 - Streamlit App
        </p>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()