"""
This file is an edited version of the one here:
https://github.com/modal-labs/modal-examples/blob/main/06_gpu_and_ml/comfyui/comfy_ui.py

This example shows you how to run a ComfyUI workspace with `modal serve`.

If you're unfamiliar with how ComfyUI works check out Scott Detweiler's tutorials on youtube
(https://www.youtube.com/watch?v=AbB33AxrcZo).
"""

import pathlib
import subprocess

import modal

COMFYUI_PORT = 8188

# ## Define container image
#
# Fun with ComfyUI begins with pre-trained model checkpoints.
# The checkpoint downloaded below is [huggingface.co/dreamlike-art/dreamlike-photoreal-2.0](https://huggingface.co/dreamlike-art/dreamlike-photoreal-2.0), but others can be used.
# The ComfyUI repository has other recommendations listed in this file:
# [notebooks/comfyui_colab.ipynb](https://github.com/comfyanonymous/ComfyUI/blob/master/notebooks/comfyui_colab.ipynb).
#
# This download function is run as the final image building step, and takes around 10 seconds to download
# the ~2.0 GiB model checkpoint.

# Mak sure the links contain /resolve/main instead of /raw/main is your are downloading from hugginface
CHECKPOINTS = [
    # "https://huggingface.co/stabilityai/stable-diffusion-2-inpainting/resolve/main/512-inpainting-ema.ckpt",
    # "https://huggingface.co/SG161222/Realistic_Vision_V5.1_noVAE/blob/main/Realistic_Vision_V5.1-inpainting.safetensors",
    # "https://huggingface.co/dreamlike-art/dreamlike-photoreal-2.0/resolve/main/dreamlike-photoreal-2.0.safetensors",
    # "https://huggingface.co/comfyanonymous/clip_vision_g/resolve/main/clip_vision_g.safetensors",
    # "https://huggingface.co/runwayml/clip_vision_g/resolve/main/clip_vision_g.safetensors",
    "https://huggingface.co/runwayml/stable-diffusion-v1-5/resolve/main/v1-5-pruned-emaonly.ckpt",
    # "https://huggingface.co/stabilityai/stable-video-diffusion-img2vid/resolve/main/svd.safetensors", # Image to video 14 frames
    "https://huggingface.co/stabilityai/stable-video-diffusion-img2vid-xt/resolve/main/svd_xt.safetensors",  # Image to vide 25 frames
]


def download_checkpoint():
    import httpx
    from tqdm import tqdm

    for url in CHECKPOINTS:
        checkpoints_directory = "/root/models/checkpoints"
        local_filename = url.split("/")[-1]
        local_filepath = pathlib.Path(checkpoints_directory, local_filename)
        local_filepath.parent.mkdir(parents=True, exist_ok=True)

        print(f"downloading {url} ...")
        with httpx.stream("GET", url, follow_redirects=True) as stream:
            total = int(stream.headers["Content-Length"])
            with open(local_filepath, "wb") as f, tqdm(
                total=total, unit_scale=True, unit_divisor=1024, unit="B"
            ) as progress:
                num_bytes_downloaded = stream.num_bytes_downloaded
                for data in stream.iter_bytes():
                    f.write(data)
                    progress.update(stream.num_bytes_downloaded - num_bytes_downloaded)
                    num_bytes_downloaded = stream.num_bytes_downloaded


VAES = [
    # "https://huggingface.co/stabilityai/stable-diffusion-2-inpainting/resolve/main/512-inpainting-ema.ckpt",
]


def download_vaes():
    import httpx
    from tqdm import tqdm

    for url in VAES:
        vaes_directory = "/root/models/vae"
        local_filename = url.split("/")[-1]
        local_filepath = pathlib.Path(vaes_directory, local_filename)
        local_filepath.parent.mkdir(parents=True, exist_ok=True)
        print(f"downloading {url} ...")
        with httpx.stream("GET", url, follow_redirects=True) as stream:
            total = int(stream.headers["Content-Length"])
            with open(local_filepath, "wb") as f, tqdm(
                total=total, unit_scale=True, unit_divisor=1024, unit="B"
            ) as progress:
                num_bytes_downloaded = stream.num_bytes_downloaded
                for data in stream.iter_bytes():
                    f.write(data)
                    progress.update(stream.num_bytes_downloaded - num_bytes_downloaded)
                    num_bytes_downloaded = stream.num_bytes_downloaded


PLUGINS = [
    {
        "url": "https://github.com/coreyryanhanson/ComfyQR",
        "requirements": "requirements.txt",
    },
    # {"url": "https://github.com/ltdrdata/ComfyUI-Manager"},
    # {
    #     "url": "https://github.com/ltdrdata/ComfyUI-Impact-Pack.git",
    #     "requirements": "requirements.txt",
    # },
]


def download_plugins():
    import subprocess

    for plugin in PLUGINS:
        url = plugin["url"]
        name = url.split("/")[-1]
        command = f"cd /root/custom_nodes && git clone {url}"
        try:
            subprocess.run(command, shell=True, check=True)
            print(f"Repository {url} cloned successfully")
        except subprocess.CalledProcessError as e:
            print(f"Error cloning repository: {e.stderr}")
        if plugin.get("requirements"):
            pip_command = f"cd /root/custom_nodes/{name} && pip install -r {plugin['requirements']}"
        try:
            subprocess.run(pip_command, shell=True, check=True)
            print(f"Requirements for {url} installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"Error installing requirements: {e.stderr}")


# Pin to a specific commit from https://github.com/comfyanonymous/ComfyUI/commits/master/
# for stability. To update to a later ComfyUI version, change this commit identifier.
comfyui_commit_sha = " e6482fbbfc83cd25add0532b2e4c51d305e8a232 "  # 2024/04/01

image = (
    modal.Image.debian_slim()
    .apt_install("git")
    # Here we place the latest ComfyUI repository code into /root.
    # Because /root is almost empty, but not entirely empty
    # as it contains this comfy_ui.py script, `git clone` won't work.
    # As a workaround we `init` inside the non-empty directory, then `checkout`.
    .run_commands(
        "cd /root && git init .",
        "cd /root && git remote add --fetch origin https://github.com/comfyanonymous/ComfyUI",
        f"cd /root && git checkout {comfyui_commit_sha}",
        "cd /root && pip install xformers!=0.0.18 -r requirements.txt --extra-index-url https://download.pytorch.org/whl/cu121",
        "cd /root && git clone https://github.com/pydn/ComfyUI-to-Python-Extension.git",
        "cd /root/ComfyUI-to-Python-Extension && pip install -r requirements.txt",
        "cd /root/ComfyUI-to-Python-Extension && pip install -r requirements.txt",
    )
    # Use fork of https://github.com/valohai/asgiproxy with bugfixes.
    .pip_install(
        "git+https://github.com/modal-labs/asgiproxy.git@ef25fe52cf226f9a635e87616e7c049e451e2bd8",
        "httpx",
        "requests",
        "tqdm",
    )
    .run_function(download_checkpoint)
    .run_function(download_vaes)
    .run_function(download_plugins)
)
stub = modal.Stub(name="ComfyUI", image=image)

# ## Start the ComfyUI server
#
# Inside the container, we will run the ComfyUI server and execution queue on port 8188. Then, we
# wrap this function in the `@web_server` decorator to expose the server as a web endpoint.
#
# For ASGI-compatible frameworks, you can also use Modal's `@asgi_app` decorator.


@stub.function(
    gpu="any",
    # Allows 100 concurrent requests per container.
    allow_concurrent_inputs=100,
    # Restrict to 1 container because we want to our ComfyUI session state
    # to be on a single container.
    concurrency_limit=1,
    keep_warm=1,
    timeout=1800,
)
@modal.web_server(8188, startup_timeout=90)
def web():
    cmd = f"python main.py --dont-print-server --listen --port {COMFYUI_PORT}"
    subprocess.Popen(cmd, shell=True)
