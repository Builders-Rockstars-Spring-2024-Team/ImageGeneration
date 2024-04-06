import subprocess

import modal

from comfyui import image, stub

COMFYUI_PORT = 8188

# server_image = image.apt_install("wget", "unzip").run_commands(*set_up_reverse_proxy)
server_image = image

# server_stub = modal.Stub(name="comfy-server", image=server_image)


@stub.function(
    gpu="any",
    allow_concurrent_inputs=100,
    concurrency_limit=1,
    keep_warm=1,
    timeout=1800,
)
@modal.web_server(8188, startup_timeout=90)
def server():
    cmd = f"python main.py --dont-print-server --listen --port {COMFYUI_PORT}"  # --listen sets the address 0.0.0.0
    subprocess.Popen(cmd, shell=True)
