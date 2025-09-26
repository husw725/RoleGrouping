#!/bin/bash
# ==== Step 1: Check if venv exists ====
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# ==== Step 2: Activate venv ====
source venv/bin/activate

# ==== Step 3: Install requirements ====
pip install --upgrade pip
pip install -r requirements.txt

# ==== Step 4: Run Streamlit ====
streamlit run appST.py