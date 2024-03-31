import subprocess

import modal

from comfy_ui import image

COMFYUI_PORT = 8188

set_up_reverse_proxy = [
    # Install rathole
    "wget https://github.com/rapiz1/rathole/releases/download/v0.5.0/rathole-x86_64-unknown-linux-gnu.zip -O /root/rathole.zip",
    "unzip /root/rathole.zip -d /root",
    "mv /root/rathole /usr/local/bin/",  # Move rathole to a directory in PATH
    "rm /root/rathole.zip",
    # Create server.toml file for rathole
    "mkdir -p /etc/rathole",
    "echo '[server]' > /etc/rathole/server.toml",
    "echo 'bind_addr = \"0.0.0.0:2333\"' >> /etc/rathole/server.toml",
    "echo '' >> /etc/rathole/server.toml",
    "echo '[server.services.comfyui]' >> /etc/rathole/server.toml",
    "echo 'token = \"icecream\"' >> /etc/rathole/server.toml",
    f"echo 'bind_addr = \"0.0.0.0:{COMFYUI_PORT}\"' >> /etc/rathole/server.toml",
    # Set permissions to 600 for security
    "chmod 600 /etc/rathole/server.toml",
    # Run rathole in the background
    "/usr/local/bin/rathole -s /etc/rathole/server.toml &",
]

server_image = image.apt_install("wget", "unzip").run_commands(*set_up_reverse_proxy)


stub = modal.Stub(name="comfy-server", image=server_image)


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
def comfyui_server():
    cmd = f"python main.py --dont-print-server --listen --port {COMFYUI_PORT}"  # --listen sets the address 0.0.0.0
    subprocess.Popen(cmd, shell=True)
