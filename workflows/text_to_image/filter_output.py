"""
Update this function based on your workflow.
"""
from json import loads
from urllib.request import urlopen
from utils.fetch_media import fetch_media


def filter_output(
    server_address: str,
    prompt_id: str,
):
    with urlopen(f"https://{server_address}/history/{prompt_id}") as response:
        output = loads(response.read())
    outputs = output[prompt_id].get("outputs") if prompt_id in output else None
    if not outputs:
        raise RuntimeError(f"Unexpected missing ComfyUI history for {prompt_id}")

    ### Update this section
    image = outputs["13"]["images"][0]
    image_data = fetch_media(
        filename=image["filename"],
        subfolder=image["subfolder"],
        folder_type=image["type"],
        server_address=server_address,
    )
    ###

    return image_data
