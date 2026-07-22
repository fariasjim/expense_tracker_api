from fastapi import APIRouter, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession
from app.models.schemas import GlobalResponseModel, NewExpense
from app.scripts.database import get_db


router = APIRouter(prefix="/e", tags=["Expenses"])


@router.get("/", response_model=GlobalResponseModel)
def health():
    return {"status": status.HTTP_200_OK, "message": "System Healthy"}


@router.post("/new", response_model=GlobalResponseModel)
def new_expense(expense: NewExpense, session: AsyncSession = Depends(get_db)):
    """Brief explanation of the function.

    Args:
        expense[NewExpense]: for validating new expense input from client.
        session[AsyncSession]: generate a new AsyncSession with the database.

    Returns:
        GlobalResponseModel: Global response model to return output to client.
    """
    pass
