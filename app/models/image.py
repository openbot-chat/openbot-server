from pydantic import BaseModel, Field
from typing import Optional, Dict, Any



class ImageGenerationRequest(BaseModel):
    prompt:str
    height=512
    width=512
    cfg_scale=7.0
    sampler="SAMPLER_K_LMS" # SAMPLER_DDIM, SAMPLER_DDPM, SAMPLER_K_EULER, SAMPLER_K_EULER_ANCESTRAL, SAMPLER_K_HEUN, SAMPLER_K_DPM_2, SAMPLER_K_DPM_2_ANCESTRAL, SAMPLER_K_LMS
    steps=50
    num_samples=1
    seed: Optional[int] = None # Integer value # Integer value
    safety=False

class ImageDescribeRequest(BaseModel):
    url: str
    provider: str = 'azure'
    language: str = "en"


class ImageDescribeResponse(BaseModel):
    text: str