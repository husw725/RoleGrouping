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

# ==== Dependency Installation ====
echo "Upgrading pip and installing dependencies..."
python3 -m pip install --user --upgrade pip
python3 -m pip install --user -r requirements.txt

# ==== Run Application ====
echo "Starting Streamlit app..."
python3 -m streamlit run app.py
