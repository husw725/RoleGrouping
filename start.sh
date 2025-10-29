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

# # ==== Pre-check: Verify venv capability ====
# echo "Checking system dependencies..."
# if ! python3 -m venv --help >/dev/null 2>&1; then
#     echo "Python virtual environment package not found. Installing prerequisites..."
#     PYTHON_VERSION=$(python3 -c "import sys; print(f'python3.{sys.version_info.minor}-venv')")
    
#     echo "Installing required system package: $PYTHON_VERSION"
#     sudo apt-get update
#     sudo apt-get install -y "$PYTHON_VERSION"
#     echo "------------------------------"
#     echo "System packages updated. Please try running the script again."
#     exit 1
# fi

# # ==== Step 1: Check if venv exists ====
# if [ ! -d ".venv" ]; then
#     echo "Creating virtual environment..."
#     python3 -m venv .venv
# fi

# # ==== Step 2: Activate venv ====
# echo "Activating virtual environment..."
# source .venv/bin/activate

# ==== Step 3: Install requirements ====
echo "Upgrading pip and installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# ==== Step 4: Run Streamlit ====
echo "Starting Streamlit app..."
streamlit run app.py

# Deactivate virtual environment when done
# deactivate
