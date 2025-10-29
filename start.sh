#!/bin/bash
set -e

# Get the directory where the script resides
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Change to script directory
echo "Changing to project directory: $SCRIPT_DIR"
cd "$SCRIPT_DIR"

# ==== Step 0: Pull latest code ====
echo "Pulling latest code..."
git pull

# ==== Step 1: Check if venv exists ====
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# ==== Step 2: Activate venv ====
echo "Activating virtual environment..."
source .venv/bin/activate

# ==== Step 3: Install requirements ====
echo "Upgrading pip and installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# ==== Step 4: Run Streamlit ====
echo "Starting Streamlit app..."
streamlit run app.py

# Deactivate virtual environment when done
deactivate
