
from fastapi import APIRouter
from models.api import Model, ModelListResponse
from datetime import datetime

router = APIRouter()

@router.post('', response_model=Model)
def create_a_model(model: Model) -> Model:
  return Model()

@router.get('/{model_owner}/{model_name}/versions', response_model=ModelListResponse)
def list_model_versions(
  model_owner: str,
  model_name: str,
) -> ModelListResponse:
  return ModelListResponse(
    items=[]
  )

@router.delete('/{model_owner}/{model_name}/versions/{version_id}', response_model=Model)
def delete_a_model(
  model_owner: str,
  model_name: str,
  version_id: str
) -> None:
  return

@router.get('/{model_owner}/{model_name}/versions/{version_id}')
def get_a_model_version(
  model_owner: str,
  model_name: str,
  version_id: str
) -> Model:
  return Model(
    id = id,
  )
