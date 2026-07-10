from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_db
from app.models.schemas import User, UserAuthRequest, UserResponse, UserRole
from app.core.security import hash_password, verify_password, create_access_token
from app.api.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["Identity & Authentication"])
COOKIE_NAME = "access_token"


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def register_account(
    payload: UserAuthRequest, db: AsyncSession = Depends(get_db)
):
    statement = select(User).where(User.email == payload.email)
    result = await db.execute(statement)
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists.",
        )

    new_user = User(
        email=payload.email,
        hashed_password=hash_password(payload.password),
        role=UserRole.CUSTOMER,
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


@router.post("/login")
async def authenticate_user(
    payload: UserAuthRequest, response: Response, db: AsyncSession = Depends(get_db)
):
    statement = select(User).where(User.email == payload.email)
    execution = await db.execute(statement)
    user = execution.scalar_one_or_none()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials supplied",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This user account has been suspended",
        )
    token_data = {"sub": str(user.id), "email": user.email, "role": user.role.value}
    token = create_access_token(data=token_data)
    response.set_cookie(
        key=COOKIE_NAME,
        value=f"Bearer {token}",
        httponly=True,
        max_age=3600,
        expires=3600,
        samesite="lax",
    )
    return {
        "message": "Authentication successful",
        "user": {"id": user.id, "email": user.email, "role": user.role},
    }


@router.post("/logout")
async def delete_cookie(response: Response):
    response.delete_cookie(key=COOKIE_NAME, httponly=True, samesite="lax")
    return {"message": "Logout Successful"}


@router.get("/me", response_model=UserResponse)
async def get_authenticated_user_profile(
    current_user: User = Depends(get_current_user),
):
    return current_user
