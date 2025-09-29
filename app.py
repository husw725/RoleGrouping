import streamlit as st
from step1_frame_check import run_step1
from step2_roles import run_step2
from step3_prompt_check import run_step3

def main():
    st.set_page_config(page_title="人物分组工具", layout="wide")

    st.sidebar.title("导航")
    step = st.sidebar.radio("选择步骤", ["Step 1 - 关键帧选取", "Step 2 - 人物分组","Step 3 - 提示词查验"])

    if step == "Step 1 - 关键帧选取":
        run_step1()
    elif step == "Step 2 - 人物分组":
        run_step2()
    elif step == "Step 3 - 提示词查验":
        run_step3()

if __name__ == "__main__":
    main()