from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from app.models.schemas import GlobalResponseModel, Signup, User, Login
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


@router.post("/login", response_model=GlobalResponseModel)
async def login(
    login: Login,
    response: Response,
    request: Request,
    session: AsyncSession = Depends(database.get_db),
):
    """
    Login function with cookie seter.
    Sets a cookie with 60 minutes expiry for authenticity operations.
    Checks if there is any cookie previously generated. if true then clear the previous one and save the new one.

    Args:
        login[Login]: Uses Login class from app.models.schemas for validating login request.
        response[Response]: Gets Response metadata for cookie operations.
        session[AsyncSession]: Depends on database.get_db to fetch a secure connection with database.

    Returns:
        GlobalResponseModel: Returns status and message to frontend letting user know their login status.
    """
    statement = select(User).where(User.email == login.email)
    execute = await session.exec(statement)
    user = execute.first()
    if not user or not auth.check_password(login.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email and password doesn't match",
        )
    token_data = {"sub": str(user.id), "email": str(user.email)}
    token = auth.generate_auth_token(data=token_data)
    response.set_cookie(
        key="access-token",
        value=f"Bearer {token}",
        expires=3600,
        max_age=3600,
        httponly=True,
        samesite="lax",
    )
    return {"status": status.HTTP_200_OK, "message": "Login successful."}


@router.post("/logout", response_model=GlobalResponseModel)
def logout(response: Response):
    """
    Deletes the cookie generated in login. This clears out the token.

    Args:
        response[Response]: fetches the response for editing before sending out to client.

    Returns:
        GlobalResponseModel: Returns status and message to user.
    """
    try:
        response.delete_cookie(key="access-token")
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No cookie found. You may not be logged in.",
        )
    return {"status": status.HTTP_200_OK, "message": "Logged out successfully!"}
