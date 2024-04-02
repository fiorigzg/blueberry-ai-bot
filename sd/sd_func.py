import io
import base64
import aiohttp
from PIL import Image, PngImagePlugin
import asyncio

from mesconstants import mesdict
from constants import isBuild


async def text_to_img(req):
  
  realReq = {
    "prompt": req["tags"],
    "negative_prompt": req["antitags"],
    "n_iter": int(req["imgCount"]),
    "steps": 30,
    "cfg_scale": int(req["scale"]),
    "width": int(req["width"]),
    "height": int(req["height"]),
    "filter_nsfw": False,
    "sampler_index": "DDIM"
  }

  if isBuild:
    async with aiohttp.ClientSession() as session:
      async with session.post(url=f'http://0.0.0.0:7860/sdapi/v1/options', json={"sd_model_checkpoint": mesdict['rus']['model']['names'][req["model"]], "sd_vae": mesdict["rus"]["model"]["vae"][req["model"]]}):
        async with session.post(url='http://0.0.0.0:7860/sdapi/v1/txt2img', json=realReq) as res:
          resJson = await res.json()

          num = 1
          imgs = []
          for i in resJson['images']:
            img = io.BytesIO(base64.b64decode(i.split(",",1)[0]))
            img.name = f'img-{num}.png'
            imgs.append(img)
            num += 1

          return imgs
  else: 
    with open("example.jpg", "rb") as image:
      await asyncio.sleep(5)
      i = base64.b64encode(image.read()).decode('utf-8')
      imgs = []
      print(int(req["imgCount"]))
      for n in range(int(req["imgCount"])):
        imgs.append(io.BytesIO(base64.b64decode(i.split(",",1)[0])))
        # print(n)
      return imgs
      
async def img_to_img(req):
  
  realReq = {
    "init_images": [req["reference"]],
    "denoising_strength": req["referenceStrength"],
    "prompt": req["tags"],
    "negative_prompt": req["antitags"],
    "n_iter": int(req["imgCount"]),
    "steps": 30,
    "cfg_scale": int(req["scale"]),
    "width": int(req["width"]),
    "height": int(req["height"]),
    "filter_nsfw": False,
    "sampler_index": "DDIM"
  }

  if isBuild:
    async with aiohttp.ClientSession() as session:
      async with session.post(url=f'http://0.0.0.0:7860/sdapi/v1/options', json={"sd_model_checkpoint": mesdict['rus']['model']['names'][req["model"]], "sd_vae": mesdict["rus"]["model"]["vae"][req["model"]]}):
        async with session.post(url='http://0.0.0.0:7860/sdapi/v1/img2img', json=realReq) as res:
          resJson = await res.json()
          num = 1
          imgs = []
          for i in resJson['images']:
            img = io.BytesIO(base64.b64decode(i.split(",",1)[0]))
            img.name = f'img-{num}.png'
            imgs.append(img)
            num += 1

          return imgs
  else: 
    with open("example.jpg", "rb") as image:
      await asyncio.sleep(5)
      i = base64.b64encode(image.read()).decode('utf-8')
      imgs = []
      for n in range(int(req["imgCount"])):
        imgs.append(io.BytesIO(base64.b64decode(i.split(",",1)[0])))
      return imgs
          
async def extra_single_img(req):
  realReq = {
    "resize_mode": 0,
    "upscaling_resize": 2,
    "upscaler_1": "R-ESRGAN 4x+",
    "image": req["image"]
  }

  if isBuild:
    async with aiohttp.ClientSession() as session:
      async with session.post(url=f'http://0.0.0.0:7860/sdapi/v1/options', json={"sd_model_checkpoint": mesdict['rus']['model']['names'][req["model"]], "sd_vae": mesdict["rus"]["model"]["vae"][req["model"]]}):
        async with session.post(url='http://0.0.0.0:7860/sdapi/v1/extra-single-image', json=realReq) as res:
          resJson = await res.json()
          img = io.BytesIO(base64.b64decode(resJson["image"].split(",",1)[0]))
          image = Image.open(io.BytesIO(base64.b64decode(resJson['image'].split(",",1)[0])))
          image.save("output.png")
          return img
  else: 
    with open("example.jpg", "rb") as image:
      await asyncio.sleep(5)
      i = base64.b64encode(image.read()).decode('utf-8')
      img = io.BytesIO(base64.b64decode(i.split(",",1)[0]))
      return img
