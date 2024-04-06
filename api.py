import json
import urllib
import uuid
import os


from modal import Image, Stub, Secret, asgi_app
from fastapi import FastAPI

# Text to image
from workflows.text_to_image.workflow import workflow as workflow_text_to_image
from workflows.text_to_image.prepare_workflow import (
    prepare_workflow as prepare_workflow_text_to_image,
)
from workflows.text_to_image.filter_output import (
    filter_output as filter_output_text_to_image,
)

# Image to image
from workflows.image_to_image.workflow import workflow as workflow_image_to_image
from workflows.image_to_image.prepare_workflow import (
    prepare_workflow as prepare_workflow_image_to_image,
)
from workflows.image_to_image.filter_output import (
    filter_output as filter_output_image_to_image,
)

# Image to video
from workflows.image_to_video.workflow import workflow as workflow_image_to_video
from workflows.image_to_video.prepare_workflow import (
    prepare_workflow as prepare_workflow_image_to_video,
)
from workflows.image_to_video.filter_output import (
    filter_output as filter_output_image_to_video,
)


stub = Stub(name="ComfyCustomApi")
image = (
    Image.debian_slim(python_version="3.12")
    .pip_install("websocket-client==1.6.4")
    .pip_install("requests")
)

with image.imports():  # These are only imported inside the container. The others are imported both locally and inside the container.
    from fastapi import Header, UploadFile, Request, Response
    import websocket


COMFYUI_SERVER_LABEL = "comfyui-web"


web_app = FastAPI()


@stub.function(image=image, secrets=[Secret.from_dotenv()])
@asgi_app()
def api():
    modal_profile = os.environ["MODAL_PROFILE"]
    # comfy_ui_server_url = (
    #     f"https://{modal_profile}--{COMFYUI_SERVER_LABEL}.modal.run"  # modal deploy
    # )
    comfy_ui_server_url = (
        f"https://{modal_profile}--{COMFYUI_SERVER_LABEL}-dev.modal.run"  # modal serve
    )
    server_address = comfy_ui_server_url.split("://")[1]
    web_app.state.server_address = server_address
    return web_app


@stub.function(image=image)
@web_app.post("/text_to_image")
async def text_to_image(
    request: Request,
    prompt: str,
    workflow_json: str = workflow_text_to_image,
    user_agent: str | None = Header(None),
):
    server_address = request.app.state.server_address
    print(server_address)

    workflow_json = json.loads(workflow_json)
    workflow_json = prepare_workflow_text_to_image(
        server_address, workflow_json, prompt=prompt
    )
    prompt_id = run_workflow(server_address, workflow_json)
    image = filter_output_text_to_image(server_address, prompt_id)
    return Response(content=image, media_type="image/jpeg")


@stub.function(image=image)
@web_app.post("/image_to_image")
async def image_to_image(
    request: Request,
    image: UploadFile,
    prompt: str | None = None,
    workflow_json: str | None = workflow_image_to_image,
    user_agent: str | None = Header(None),
):
    server_address = request.app.state.server_address
    input_image = await image.read()
    workflow_json = json.loads(workflow_json)
    workflow_json = prepare_workflow_image_to_image(
        server_address, workflow_json, prompt=prompt, image=input_image
    )
    prompt_id = run_workflow(server_address, workflow_json)
    image = filter_output_image_to_image(server_address, prompt_id)
    return Response(content=image, media_type="image/jpeg")


@stub.function(image=image)
@web_app.post("/image_to_video")
async def image_to_video(
    request: Request,
    image: UploadFile,
    prompt: str | None = None,
    workflow_json: str | None = workflow_image_to_video,
    user_agent: str | None = Header(None),
):
    server_address = request.app.state.server_address
    input_image = await image.read()
    workflow_json = json.loads(workflow_json)
    workflow_json = prepare_workflow_image_to_video(
        server_address, workflow_json, prompt=prompt, image=input_image
    )
    prompt_id = run_workflow(server_address, workflow_json)
    image = filter_output_image_to_video(server_address, prompt_id)
    return Response(content=image, media_type="image/jpeg")


def run_workflow(server_address: str, workflow_json: str):
    data = {"prompt": workflow_json}
    # Connect via websocket
    client_id = str(uuid.uuid4())
    ws_address = f"wss://{server_address}/ws?clientId={client_id}"
    ws = websocket.WebSocket()
    print(f"Connecting to websocket at {ws_address} ...")
    ws.connect(ws_address)
    print(f"Connected at {ws_address}. Running workflow via API")
    data["client_id"] = client_id
    # Request to run workflow
    data = json.dumps(data).encode("utf-8")
    req = urllib.request.Request("https://{}/prompt".format(server_address), data=data)
    response_data = json.loads(urllib.request.urlopen(req).read())
    # Listen for updates
    prompt_id = response_data["prompt_id"]
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
    # Return id to fetch results
    return prompt_id
