"""
Requires wget and unzip on the image
...
I haven't actually tested that this works.
I thought I needed it but realized I didn't when I was about to use it.
It would be useful if one were to secure the ComfyUI service from the internet and only connect to it through their api running in another container.
"""

password = "An_easy_password"

set_up_reverse_proxy_client = [
    # Install rathole https://github.com/rapiz1/rathole
    "wget https://github.com/rapiz1/rathole/releases/download/v0.5.0/rathole-x86_64-unknown-linux-gnu.zip -O /root/rathole.zip",
    "unzip /root/rathole.zip -d /root",
    "mv /root/rathole /usr/local/bin/",  # Move rathole to a directory in PATH
    "rm /root/rathole.zip",
    # Create server.toml file for rathole
    "mkdir -p /etc/rathole",
    "echo '[client]' > /etc/rathole/client.toml",
    "echo 'bind_addr = \"0.0.0.0:2333\"' >> /etc/rathole/client.toml",
    "echo '' >> /etc/rathole/client.toml",
    "echo '[client.services.comfyui]' >> /etc/rathole/client.toml",
    "echo f'token = \"{password}\"' >> /etc/rathole/client.toml",
    "echo 'bind_addr = \"127.0.0.1:8000\"' >> /etc/rathole/client.toml",
    # Set permissions to 600 for security
    "chmod 600 /etc/rathole/client.toml",
    # Run rathole in the background
    "/usr/local/bin/rathole /etc/rathole/client.toml &",
]

COMFYUI_PORT = 8188

set_up_reverse_proxy_server = [
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
    "echo f'token = \"{password}\"' >> /etc/rathole/server.toml",
    f"echo 'bind_addr = \"0.0.0.0:{COMFYUI_PORT}\"' >> /etc/rathole/server.toml",
    # Set permissions to 600 for security
    "chmod 600 /etc/rathole/server.toml",
    # Run rathole in the background
    "/usr/local/bin/rathole /etc/rathole/server.toml &",
]
