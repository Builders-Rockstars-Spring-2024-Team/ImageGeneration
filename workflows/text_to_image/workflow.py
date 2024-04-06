# To avoid mounting the json file in the container
# Make sure there are no backslashes as in \n
workflow = """
{
  "1": {
    "inputs": {
      "ckpt_name": "v1-5-pruned-emaonly.ckpt"
    },
    "class_type": "CheckpointLoaderSimple",
    "_meta": {
      "title": "Load Checkpoint"
    }
  },
  "2": {
    "inputs": {
      "text": "a bag of wooden blocks",
      "clip": ["1", 1]
    },
    "class_type": "CLIPTextEncode",
    "_meta": {
      "title": "CLIP Text Encode (Prompt)"
    }
  },
  "3": {
    "inputs": {
      "text": "bag of noodles",
      "clip": ["1", 1]
    },
    "class_type": "CLIPTextEncode",
    "_meta": {
      "title": "CLIP Text Encode (Prompt)"
    }
  },
  "4": {
    "inputs": {
      "seed": 232824767484224,
      "steps": 12,
      "cfg": 8,
      "sampler_name": "euler",
      "scheduler": "normal",
      "denoise": 1,
      "model": ["1", 0],
      "positive": ["2", 0],
      "negative": ["3", 0],
      "latent_image": ["5", 0]
    },
    "class_type": "KSampler",
    "_meta": {
      "title": "KSampler"
    }
  },
  "5": {
    "inputs": {
      "width": 512,
      "height": 512,
      "batch_size": 1
    },
    "class_type": "EmptyLatentImage",
    "_meta": {
      "title": "Empty Latent Image"
    }
  },
  "6": {
    "inputs": {
      "samples": ["8", 0],
      "vae": ["1", 2]
    },
    "class_type": "VAEDecode",
    "_meta": {
      "title": "VAE Decode"
    }
  },
  "8": {
    "inputs": {
      "add_noise": "enable",
      "noise_seed": 395748023703486,
      "steps": 30,
      "cfg": 8,
      "sampler_name": "euler",
      "scheduler": "karras",
      "start_at_step": 12,
      "end_at_step": 10000,
      "return_with_leftover_noise": "disable",
      "model": ["1", 0],
      "positive": ["2", 0],
      "negative": ["3", 0],
      "latent_image": ["10", 0]
    },
    "class_type": "KSamplerAdvanced",
    "_meta": {
      "title": "KSampler (Advanced)"
    }
  },
  "10": {
    "inputs": {
      "upscale_method": "nearest-exact",
      "scale_by": 2,
      "samples": ["4", 0]
    },
    "class_type": "LatentUpscaleBy",
    "_meta": {
      "title": "Upscale Latent By"
    }
  },
  "13": {
    "inputs": {
      "filename_prefix": "ComfyUI",
      "images": ["6", 0]
    },
    "class_type": "SaveImage",
    "_meta": {
      "title": "Save Image"
    }
  }
}
"""
