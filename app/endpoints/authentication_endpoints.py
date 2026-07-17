from fastapi import APIRouter, Depends
from sqlmodel import Session
from app.models.schemas import GlobalResponseModel, Signup
from app.scripts import database, authentication

router = APIRouter(prefix="/u", tags=["Authentication"])


@router.post("/signup", response_model=GlobalResponseModel)
def signup(request: Signup, session: Session = Depends(database.get_db)):
    """
    To let users to signup with their information. this should
    hash and save their information in database.

    Args:
        request[Signup]: uses pydantic basemodel from app.models.schemas to validate user information.
        session[Session]: Depends on get_db to open a connection to database.

    Returns:
        GlobalResponseModel: Returns status and message to frontend letting user know their signup status.
    """
    pass
