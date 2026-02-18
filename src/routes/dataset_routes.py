from fastapi import APIRouter, Depends, Request
from typing import List

from src.schemas.dataset_schemas.dataset_response_model import DatasetResponseModel
from src.services.dataset_service import DatasetService

router = APIRouter(
    prefix="/datasets",
    tags=["datasets"],
)


def get_dataset_service(request: Request) -> DatasetService:
    return request.app.state.dataset_service


@router.get("/", response_model=List[DatasetResponseModel])
def list_datasets(
    dataset_service: DatasetService = Depends(get_dataset_service),
) -> List[DatasetResponseModel]:
    return [DatasetResponseModel(**d) for d in dataset_service.get_dataset_summaries()]
