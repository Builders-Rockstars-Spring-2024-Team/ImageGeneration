import json
import urllib
import uuid
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Header

# from fastapi.responses import JSONResponse
from modal import Image, Stub, Volume, asgi_app


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
    "echo 'local_addr = \"127.0.0.1:8000\"' >> /etc/rathole/server.toml",
    # Set permissions to 600 for security
    "chmod 600 /etc/rathole/server.toml",
    # Run rathole in the background
    "/usr/local/bin/rathole -s /etc/rathole/server.toml &",
]


web_app = FastAPI()
stub = Stub(name="comfy-api")
image = (
    Image.debian_slim(python_version="3.10")
    .pip_install("websocket-client==1.6.4")
    .pip_install("requests")
    # .apt_install("wget", "unzip")
    # .run_commands(*set_up_reverse_proxy)
)


VOLUME_NAME = "comfyui-workflow"
volume = Volume.from_name(VOLUME_NAME)
VOL_MOUNT_PATH = Path("/vol")
VOL_MOUNT_WORKFLOW_PATH = VOL_MOUNT_PATH / "img2img.json"

COMFYUI_SERVER_PORT = "8188"
COMFYUI_SERVER_URL = "https://pbvrct--comfy-server-comfyui-server-dev.modal.run"


def run_workflow(ws, prompt: str, server_address: str, client_id: str) -> list[bytes]:
    p = {"prompt": prompt, "client_id": client_id}
    data = json.dumps(p).encode("utf-8")
    req = urllib.request.Request("https://{}/prompt".format(server_address), data=data)
    response_data = json.loads(urllib.request.urlopen(req).read())
    prompt_id = response_data["prompt_id"]
    output_images = {}

    while True:
        out = ws.recv()
        if isinstance(out, str):
            print(f"recieved str msg from websocket. ws msg: {out}")
            try:
                message = json.loads(out)
            except json.JSONDecodeError:
                print(f"expected valid JSON but got: {out}")
                raise
            print(f"received msg from ws: {message}")
            if message["type"] == "executing":
                data = message["data"]
                if data["node"] is None and data["prompt_id"] == prompt_id:
                    break  # Execution is done!
        else:
            continue  # previews are binary data

    # Fetch workflow execution history, which contains references to our completed images.
    with urllib.request.urlopen(
        f"https://{server_address}/history/{prompt_id}"
    ) as response:
        output = json.loads(response.read())
    history = output[prompt_id].get("outputs") if prompt_id in output else None
    if not history:
        raise RuntimeError(f"Unexpected missing ComfyUI history for {prompt_id}")
    for node_id in history:
        node_output = history[node_id]
        if "images" in node_output:
            images_output = []
            for image in node_output["images"]:
                image_data = fetch_image(
                    filename=image["filename"],
                    subfolder=image["subfolder"],
                    folder_type=image["type"],
                    server_address=server_address,
                )
                images_output.append(image_data)
        output_images[node_id] = images_output
    return output_images


def fetch_image(
    filename: str, subfolder: str, folder_type: str, server_address: str
) -> bytes:
    data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
    url_values = urllib.parse.urlencode(data)
    with urllib.request.urlopen(
        "https://{}/view?{}".format(server_address, url_values)
    ) as response:
        return response.read()


@stub.function(image=image)
@web_app.post("/generate")
async def handle_root(
    user_agent: Optional[str] = Header(None),
    image_bytes=None,
    prompt="A glass withh flowers",
):
    import os
    import websocket
    from fastapi import Response
    import requests

    volume.reload()

    with open(VOL_MOUNT_WORKFLOW_PATH, "r") as file:
        workflow_data = json.load(file)

    server_address = COMFYUI_SERVER_URL.split("://")[1]  # strip protocol
    client_id = str(uuid.uuid4())
    ws_address = f"wss://{server_address}/ws?clientId={client_id}"

    # Save the image
    filename = "office.jpg"
    save_directory = "/path/to/save/directory"
    file_path = os.path.join(save_directory, filename)
    with open(file_path, "wb") as file:
        file.write(await image_bytes.read())
    # Send the image to the server
    data = {"subfolder": "your_subfolder"}
    files = {"image": open(file_path, "rb")}
    resp = requests.post(
        "https://{}/upload/image".format(server_address), files=files, data=data
    )
    print(resp.content)
    # Update the workflow data
    workflow_data["6"]["inputs"]["text"] = prompt
    workflow_data["10"]["inputs"]["image"] = filename

    # Call the server

    ws = websocket.WebSocket()
    print(f"Connecting to websocket at {ws_address} ...")
    ws.connect(ws_address)
    print(f"Connected at {ws_address}. Running workflow via API")
    images = run_workflow(ws, workflow_data, server_address, client_id)
    image_list = []
    for node_id in images:
        for image_data in images[node_id]:
            image_list.append(image_data)
    # print(image_list)

    # encoded_images = []
    # for image_data in response:
    #     encoded_image = base64.b64encode(image_data).decode("utf-8")
    #     encoded_images.append(encoded_image)
    # response_data = {"images": encoded_images}
    # return JSONResponse(content=response_data)

    return Response(
        content=image_list,
        media_type="image/jpeg",
    )


@stub.function(
    image=image,
    volumes={VOL_MOUNT_PATH: volume},
)
@asgi_app()
def fastapi_app():
    return web_app
