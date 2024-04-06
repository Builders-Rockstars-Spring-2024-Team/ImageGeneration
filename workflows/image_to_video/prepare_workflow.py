"""
Update this function based on your workflow.
"""
from typing import Optional
from utils.send_image import send_image


def prepare_workflow(
    server_address: str,
    workflow_json: dict,
    prompt: Optional[str] = None,
    negative_prompt: Optional[str] = None,
    image: Optional[bytes] = None,
):
    workflow_json = send_image(image, server_address, workflow_json, image_node=23)

    return workflow_json
