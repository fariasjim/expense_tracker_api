from fastapi import APIRouter, Depends, HTTPException, status
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
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with the same email exist. Please login or use a different email.",
        )
    password_hashed = auth.hash_password(password=request.password)
    new_user = User(
        **request.model_dump(exclude={"password"}), password=password_hashed
    )
    session.add(new_user)
    try:
        await session.commit()
        await session.refresh(new_user)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}.",
        )
    return {
        "status": status.HTTP_201_CREATED,
        "message": f"Signup successfull for user: {new_user.name} with id-{new_user.id}. Please login to access your account.",
    }
