# Instructions

Prerequisites:

- Create a modal account
- Create a virtual environment: `python3 -m venv .venv`
- Install the libraries inside requirements.txt: `pip install -r requirements.txt`

## Serve the ComfyUI on cloud GPUs:

1. `.venv\Scripts\activate`
2. `modal serve comfy_ui.py`

## Export ComfyUI workflows to deploy them on an api:

1. On ComfyUI, click on the settings wheel.
2. Check enable dev options. Outside settings you should now see Save to Api format
3. Click on Save to Api format.

## Save a workflow to a volume using the Modal CLI:

```bash
modal volume create comfyui-workflow
modal volume put comfyui-workflow workflows/img2img.json
```

## Serve the API

```
modal server comfy_server.py
modal server api.py
```

Go to the api root route on the browser's address bar

## Deploy the API

```
modal deploy comfy_server.py
modal deploy api.py
```

## Test the api

```bash
curl -X POST -F "image_bytes=@/home/username/projects/BuildersRockstars_ImageGeneration/images/office.png" -F "prompt=Workers in an office" https://pbvrct--comfy-api-fastapi-app-dev.modal.run/generate
```
