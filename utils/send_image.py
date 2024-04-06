import uuid
import tempfile

import requests


def send_image(image: bytes, server_address: str, workflow_json: dict, image_node: int):
    """
    Send an image to be used as a workflow input.
    Sends it to the server running the ComfyUI service, in advance of running the workflow.
    """
    url = "https://{}/upload/image".format(server_address)
    subfolder_in_comfyui_server = ""
    data = {"subfolder": subfolder_in_comfyui_server, "overwrite": "true"}
    filename = f"{uuid.uuid4()}.jpg"
    # Write the image bytes to a temporary file
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(image)
        temp_file_path = temp_file.name
    # Open the temporary file in binary mode
    with open(temp_file_path, "rb") as file:
        files = {"image": (filename, file)}
        resp = requests.post(url, files=files, data=data)
    if resp.status_code != 200:
        print(f"{resp.status_code} - {resp.reason}")
    workflow_json[f"{image_node}"]["inputs"]["image"] = filename
    return workflow_json
