import os
import io
from fastapi import APIRouter, Depends
from fastapi.responses import Response
from models.image import ImageGenerationRequest, ImageDescribeRequest, ImageDescribeResponse
from PIL import Image
import requests
import base64
from services.image_service import ImageService
from core.image.image_cognitive_manager import ImageCognitiveManager


router = APIRouter()

os.environ['STABILITY_KEY'] = 'sk-wMji4Pp07mgaT9ql5ygzmltriMGD931xyOWzubfhjD7AKT9P'



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
  
    engine_id = "stable-diffusion-v1-5"

    api_host = "https://api.stability.ai"

    url = f"{api_host}/v1/generation/{engine_id}/text-to-image"
    response = requests.post(
        url,
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {os.environ['STABILITY_KEY']}",
        },
        json={
            "height": params.height,
            "width": params.width,
            "text_prompts": [{
                "text": params.prompt,
                "weight": 0.5
            }]
        }
    )

    if response.status_code != 200:
        raise Exception("Non-200 response: " + str(response.text))

    data = response.json()

    image = None
    for i, artifact in enumerate(data["artifacts"]):
        if artifact['finishReason'] == "SUCCESS":
            image = Image.open(io.BytesIO(base64.b64decode(artifact['base64'])))
    return image


def imageToByteArray(image: Image) -> bytes:
    imgByteArr = io.BytesIO()
    image.save(imgByteArr, format="png")
    imgByteArr = imgByteArr.getvalue()
    return imgByteArr



@router.post('/describe', response_model=ImageDescribeResponse)
async def analyze(
    req: ImageDescribeRequest,
    image_cognitive_mangager: ImageCognitiveManager = Depends(ImageCognitiveManager),
):
    text = await image_cognitive_mangager.describe(req.provider, req.url, req.language)
    return ImageDescribeResponse(text=text)