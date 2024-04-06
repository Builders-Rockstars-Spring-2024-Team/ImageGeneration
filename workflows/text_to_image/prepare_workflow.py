"""
Update this function based on your workflow.
"""
from typing import Optional


def prepare_workflow(
    server_address: str,
    workflow_json: dict,
    prompt: Optional[str] = None,
    negative_prompt: Optional[str] = None,
    image: Optional[bytes] = None,
):
    workflow_json["2"]["inputs"]["text"] = prompt
    workflow_json["3"]["inputs"]["text"] = "naked, nude"  # negative prompt

    return workflow_json
