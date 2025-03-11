
from fastapi import APIRouter
from models.api import PredictionRequest, Prediction, PredictionListResponse
from datetime import datetime

router = APIRouter()

@router.post('', response_model=Prediction)
def create(
  req: PredictionRequest,
) -> Prediction:
  # run
  return Prediction(
  )

@router.get('/{id}', response_model=Prediction)
def get(id: str) -> Prediction:
  return Prediction(
    id=id,
    version = "feffe",
    urls = {},
    created_at = datetime.now(),
    started_at = datetime.now(),
    completed_at = datetime.now(),
    source = "web",
    status = 'succeeded'
  )

@router.post('/{id}/cancel', response_model=Prediction)
def cancel_a_prediction(id: str) -> Prediction:
  return Prediction(
    id=id,
  )

@router.get('', response_model=PredictionListResponse)
def list_predictions() -> PredictionListResponse:
  return PredictionListResponse(
    items=[]
  )