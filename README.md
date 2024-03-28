# Instructions to serve the ComfyUI on cloud GPUs:

Prerequisites:

- Create a virtual environment: `python3 -m venv .venv`
- Install the libraries inside requirements.txt: `pip install -r requirements.txt`

Steps:

1. Open a terminal.
2. Move to the project folder: `cd ~/projects/ImageGeneration`
3. Activate the virtual environment, on Window: `.venv\Scripts\activate`
4. Serve ComfyUI: `modal serve comfy_ui.py`
