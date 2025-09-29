@echo off
REM ==== Step 0: Pull latest code ====
echo Pulling latest code...
git pull

REM ==== Step 1: Check if venv exists ====
IF NOT EXIST venv (
    echo Creating virtual environment...
    python -m venv venv
)

REM ==== Step 2: Activate venv ====
call venv\Scripts\activate

REM ==== Step 3: Install requirements ====
echo Upgrading pip...
pip install --upgrade pip
echo Installing dependencies...
pip install -r requirements.txt

REM ==== Step 4: Run Streamlit ====
echo Starting Streamlit app...
streamlit run app.py