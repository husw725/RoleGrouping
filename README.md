# RoleGrouping Project

## Description
This project appears to be a multi-step workflow for processing video frames, likely involving face detection, role assignment, and prompt checking. The `stepX_` scripts suggest a sequential process.

## Setup
To set up the project, follow these steps:

1.  **Clone the repository (if applicable):**
    ```bash
    git clone <repository-url>
    cd RoleGrouping
    ```

2.  **Create and activate a virtual environment (recommended):**
    ```bash
    python -m venv venv
    # On Windows
    .\venv\Scripts\activate
    # On macOS/Linux
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Usage

To run the application, use the provided start scripts:

*   **On Windows:**
    ```bash
    start.bat
    ```

*   **On macOS/Linux:**
    ```bash
    bash start.sh
    ```

## Workflow
The project seems to follow a series of steps:

*   `step0_scene_extra.py`: Likely for extracting scenes or initial video processing.
*   `step1_frame_check.py`: Possibly for checking frames or initial analysis.
*   `step2_roles.py`: This script probably handles role assignment or grouping.
*   `step3_prompt_check.py`: Suggests a final verification or prompt-related processing.

More detailed information would require examining the individual scripts.