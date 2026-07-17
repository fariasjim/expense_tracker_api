from fastapi import APIRouter, Depends, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from app.models.schemas import GlobalResponseModel, Signup, User
from app.scripts import database, authentication

router = APIRouter(prefix="/u", tags=["Authentication"])
auth = authentication.Authentication()


@router.post("/signup", response_model=GlobalResponseModel)
async def signup(request: Signup, session: AsyncSession = Depends(database.get_db)):
    """
    To let users to signup with their information. this should
    hash and save their information in database.

    Args:
        request[Signup]: uses pydantic basemodel from app.models.schemas to validate user information.
        session[Session]: Depends on get_db to open a connection to database.

    Returns:
        GlobalResponseModel: Returns status and message to frontend letting user know their signup status.
    """
    statement = select(User).where(User.email == request.email)
    execute = await session.exec(statement)
    existing_user = execute.first()
    if existing_user:
        return {
            "status": status.HTTP_400_BAD_REQUEST,
            "message": "An account with the same email exists. Try using a different email instead.",
        }
    request.password = auth.hash_password(password=request.password)
    session.add(request)
    try:
        await session.commit()
        await session.refresh(request)
    except Exception as e:
        return {
            "status": status.HTTP_408_REQUEST_TIMEOUT,
            "message": f"Exception occured. {e}",
        }
    return {
        "status": status.HTTP_201_CREATED,
        "message": "Signup successfull. Please login to access your account.",
    }
