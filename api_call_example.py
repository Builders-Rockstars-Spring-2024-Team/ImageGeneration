import datetime

import requests

# Inputs
model = "stable-image/edit/inpaint"
prompt = "People having fun in the conference room"
image = "/home/username/projects/builders_demo/images/office.jpeg"
image_mask = "/home/username/projects/builders_demo/images/workers_having_fun.jpeg"

api_key = "sk-fCDp0qmmP7zWpRmvIEMO8YXDXcNWLm4o6bPQQfp7IuAbP3Qt"

# Request
api_url = f"https://api.stability.ai/v2beta/{model}"
headers = {"authorization": f"Bearer {api_key}", "accept": "image/*"}
files = {"image": open(image, "rb"), "mask": open(image_mask, "rb")}
data = {"prompt": prompt, "output_format": "webp"}
response = requests.post(api_url, headers=headers, files=files, data=data)

# Response
if response.status_code == 200:
    timestamp = datetime.datetime.now().isoformat()
    with open(f"images/{timestamp}.jpg", "wb") as file:
        file.write(response.content)
else:
    print("Error:", response.json())
