from fastapi import APIRouter, status
from app.models.schemas import GlobalResponseModel


router = APIRouter(prefix="/e", tags=["Expenses"])


@router.get("/", response_model=GlobalResponseModel)
def health():
    return {"status": status.HTTP_200_OK, "message": "System Healthy"}
