import streamlit as st
from step0_scene_extra import run_step0
from step1_frame_check import run_step1
from step2_roles import run_step2
from step3_prompt_check import run_step3

def main():
    # Page configuration
    st.set_page_config(
        page_title="Character Grouping Tool",
        layout="wide",
        page_icon="🧩",
        initial_sidebar_state="expanded"
    )

    # Sidebar styling
    st.sidebar.markdown(
        "<h2 style='color:#4B8BBE;'>📌 Navigation</h2>", 
        unsafe_allow_html=True
    )

    step = st.sidebar.radio(
        "Select Step",
        [
            "Step0 - Video Scene Segmentation",
            "Step1 - Keyframe Selection",
            "Step2 - Character Grouping",
            "Step3 - Prompt Verification"
        ],
        index=0,
        key="step_radio",
        label_visibility="visible"
    )

    # Content routing
    if step == "Step0 - Video Scene Segmentation":
        run_step0()
    elif step == "Step1 - Keyframe Selection":
        run_step1()
    elif step == "Step2 - Character Grouping":
        run_step2()
    elif step == "Step3 - Prompt Verification":
        run_step3()

    # Footer styling
    st.markdown(
        """
        <hr style='height:1px;border:none;color:#ddd;background-color:#ddd;'/>
        <p style='text-align:center;color:#999;font-size:12px;'>
            &copy; 2025 Character Grouping Tool - Streamlit App
        </p>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
