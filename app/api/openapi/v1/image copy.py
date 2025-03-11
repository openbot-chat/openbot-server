import os
import io
from fastapi import APIRouter
from fastapi.responses import Response
from models.image import ImageGenerationRequest
from models.chat import ChatMessage
from stability_sdk import client
import stability_sdk.interfaces.gooseai.generation.generation_pb2 as generation
from PIL import Image
import warnings


router = APIRouter()

os.environ['STABILITY_KEY'] = 'sk-wMji4Pp07mgaT9ql5ygzmltriMGD931xyOWzubfhjD7AKT9P'

stability_api = client.StabilityInference(
  key=os.environ['STABILITY_KEY'], 
  verbose=True,
)

@router.post('/generate')
async def generate(
  req: ImageGenerationRequest
):
  image = generate_image(req)
  if (isinstance(image, str)):
      return Response(content=image, status_code=500)
  imageAsBytes = imageToByteArray(image)
  return Response(imageAsBytes, media_type="image/png")

def generate_image(params: ImageGenerationRequest):
  seed = None
  if (params.seed):
      seed = [int(x) for x in str(params.seed)]
  
  answers = stability_api.generate(
      prompt=params.prompt,
      height=params.height,
      width=params.width,
      cfg_scale=params.cfg_scale,
      sampler=params.sampler,
      steps=params.steps,
      seed=seed
  )
  
  image = None
  
  for resp in answers:
      for artifact in resp.artifacts:
          if artifact.finish_reason == generation.FILTER:
              warnings.warn(
                  "Your request activated the API's safety filters and could not be processed."
                  "Please modify the prompt and try again.")
              return "Your request activated the API's safety filters and could not be processed."
          if artifact.type == generation.ARTIFACT_IMAGE:
              image = Image.open(io.BytesIO(artifact.binary))  
  return image

def imageToByteArray(image: Image) -> bytes:
  imgByteArr = io.BytesIO()
  image.save(imgByteArr, format="png")
  imgByteArr = imgByteArr.getvalue()
  return imgByteArr