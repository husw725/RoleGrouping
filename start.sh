#!/bin/bash

# ==== Step 0: Pull latest code ====
echo "Pulling latest code..."
git pull

# ==== Step 1: Check if venv exists ====
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# ==== Step 2: Activate venv ====
echo "Activating virtual environment..."
source venv/bin/activate

# ==== Step 3: Install requirements ====
echo "Upgrading pip and installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# ==== Step 4: Run Streamlit ====
echo "Starting Streamlit app..."
streamlit run app.py