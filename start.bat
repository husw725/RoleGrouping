@echo off
REM ==== Step 1: Check if venv exists ====
IF NOT EXIST venv (
    echo Creating virtual environment...
    python -m venv venv
)

REM ==== Step 2: Activate venv ====
call venv\Scripts\activate

REM ==== Step 3: Install requirements ====
pip install --upgrade pip
pip install -r requirements.txt

REM ==== Step 4: Run Streamlit ====
streamlit run app.py