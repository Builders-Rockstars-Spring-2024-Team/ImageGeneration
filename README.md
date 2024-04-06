We run the ComfyUI software on cloud GPUs using Modal Labs. It allows us to use the GUI without GPUs on our machines.

We also deploy ComfyUI to run workflows programatically, through Api calls.

For ease of use, we add a FastAPI Api in front of the ComfyUI Api.

# Instructions

## Prerequisites:

- Clone this repository and cd into it (If you don't have git, instead of git clone you can just copy the code into a folder and move into it):

```
git clone https://github.com/Builders-Rockstars-Spring-2024-Team/ImageGeneration.git
cd ImageGeneration
```

- Create a modal account and follow their instructions to set up a token.
- Optional: Create and activate a python virtual environtment:

```
python3 -m venv .venv
.venv\Scripts\activate (Windows)
source .venv/bin/activate (Mac/Linux)
```

- Install the libraries inside requirements.txt:

```bash
pip install -r requirements.txt
```

## Serve the ComfyUI GUI on cloud GPUs:

```bash
modal serve comfyui.py
```

Get the UI url from the apps section of the modal dashboard.

By using `modal serve` the app will stop when you press `Ctrl-C` on your shell.

## Deploy the Api

```
modal deploy comfyui.py
```

Export the modal profile to an `.env` file.

```bash
# Linux, Mac
echo "MODAL_PROFILE=$(modal profile current)" > .env
# Windows PowerShell
"MODAL_PROFILE=$(modal profile current)" | Out-File -FilePath .env (Windows PowerShell)
# Windows command prompt
echo MODAL_PROFILE^%modal profile current^% > .env
```

Then:

```
modal deploy api.py
```

To shut the comfyui and the api down, find the `Stop` buttons on the modal apps dashboard.

## Test the Api

```bash
MODAL_PROFILE=$(modal profile current)
```

- Text to image:

```bash
curl -X "POST" "https://$MODAL_PROFILE--comfycustomapi-api-dev.modal.run/text_to_image?prompt=Workers%20wearing%20white%20shirts" --output images/text_to_image_output.png
```

- Image to image:

```bash
curl -X POST -F "image=@images/office.png' 'https://$MODAL_PROFILE--comfycustomapi-api-dev.modal.run/image_to_image?prompt=Workers%20wearing%20white%20shirts" --output images/image_to_image_output.jpg
```

- Image to video:

```bash
curl -X POST -F "image=@images/office.png" "https://$MODAL_PROFILE--comfycustomapi-api-dev.modal.run/image_to_video" --output images/image_to_video_output.webp
```

## Deploy your own ComfyUI workflows to the Api

Step 1: Export them from ComfyUI:

1. On ComfyUI, click on the settings wheel.
2. Check `Enable Dev Mode Options`.
3. Outside the settings you should now see a `Save (API Format)` button. Click it.

Step 2: Add them to the Api:

1. Add a new subfolder inside the workflows folder following the already existing examples.
2. Add a new route inside `api.py`.
3. Redeploy the Api.

## Serve the Api (for debugging)

```
modal serve comfyui.py
```

Make sure the `MODAL_PROFILE` variable is inside the `.env` file.
<br>
Uncomment the `COMFYUI_SERVER_URL` variable inside `api.py`.
<br>
Then:

```
modal serve api.py
```

## Notes

There's no authentication, both the UI and the API are open to the internet. Check out the Modal docs for how to implement it.

## Disclaimer

I finished this after the hackathon deadline.

# Useful resources:

- [ComfyUI-to-Python-Extension](https://github.com/pydn/ComfyUI-to-Python-Extension/tree/main):
  This extension turns your ComfyUI workflow into Python code, sparing the need to deploy both the server and the Api. Check [this](https://modal.com/blog/comfyui-prototype-to-production) blogpost for more info.
  <br>
  The blogpost was published 2 days after the hackathon ended. Had I found out about the extension beforehand, I would have tried to use it.
- [Replicate.com](https://replicate.com/): A SaaS to run the models from api endpoints without the need to set up this infrastructure. I found out about it midway through the hackathon, tried it for a few minutes, got an error with the ComfyUI version, and went back to setting this up.
