import jwt
from fastapi import Request, Depends, HTTPException, status
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_db
from app.models.schemas import User, UserRole
from app.core.security import SECRET_KEY, ALGORITHM

COOKIE_NAME = "access_token"


async def get_current_user(
    request: Request, db: AsyncSession = Depends(get_db)
) -> User:
    token_cookie = request.cookies.get(COOKIE_NAME)
    if not token_cookie:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Missing session cookie.",
        )
    try:
        token = token_cookie.split(" ")[1] if " " in token_cookie else token_cookie
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        user_id = str(payload.get("sub"))
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid session authentication signature",
            )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session timeout. Please log in again.",
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials securely.",
        )
    statement = select(User).where(User.id == int(user_id))
    result = await db.execute(statement)
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session error. credentials mismatch.",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This account is deactivated by admin.",
        )
    return user


class RoleChecker:
    def __init__(self, allowed_roles: list[UserRole]) -> None:
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Access Denied"
            )
        return current_user
