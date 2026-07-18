from typing import Optional
from datetime import timedelta, datetime, timezone
from fastapi import Request, Depends, HTTPException, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from app.models.schemas import User
from app.scripts.database import get_db
import jwt
import bcrypt
import os

SECRETKEY: str = os.getenv(key="SECRETKEY", default="mYseCretKey")


class Authentication:
    # Used for authentication functions all over the application.
    def hash_password(self, password: str) -> str:
        """
        Hashes the given password.
        Uses a auto generated salt for secure password hashing.
        """
        byte_password: bytes = password.encode("utf-8")
        salt: bytes = bcrypt.gensalt()
        hashed_password: bytes = bcrypt.hashpw(byte_password, salt)
        return hashed_password.decode("utf-8")

    def check_password(self, given_password: str, password_from_db: str) -> bool:
        """Validating hashed password from db against the given password and return boolean value (True/False)"""
        byte_given_password: bytes = given_password.encode("utf-8")
        byte_password_from_db: bytes = password_from_db.encode("utf-8")
        return bcrypt.checkpw(byte_given_password, byte_password_from_db)

    def generate_auth_token(
        self, data: dict, expiration: Optional[timedelta] = None
    ) -> str:
        """
        Checks if the expiration time [Optional[timedelta]] is given while calling the function.
        If given, set expire_time = current time + expiration[minutes]
        If not, set expire_time = current time + 60 minutes
        then, encode a JWToken with data[dict] given.
        """
        payload: dict = data.copy()
        if expiration:
            expire_time: datetime = datetime.now(timezone.utc) + expiration
        else:
            expire_time: datetime = datetime.now(timezone.utc) + timedelta(minutes=60)
        payload.update({"exp": int(expire_time.timestamp())})
        token = jwt.encode(payload=payload, key=SECRETKEY, algorithm="HS256")
        return token

    async def get_current_user(
        self, request: Request, session: AsyncSession = Depends(get_db)
    ) -> User:
        """
        Gets the current logged in user info for authentication purposes.

        Args:
            self: self-explanatory.
            request[Request]: gets the request info.
            session[AsyncSession]: gets the database session securely.

        Returns:
            User: Returns user object for authentication check.
        """
        token_cookie = request.cookies.get("access-token")
        if not token_cookie:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required. Missing session cookie.",
            )
        try:
            token = token_cookie.split(" ")[1] if " " in token_cookie else token_cookie
            payload = jwt.decode(token, key=SECRETKEY, algorithms="HS256")
            user_id = str(payload.get("sub"))
            if user_id is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid session authentication signature. Fabricated ?",
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
        execute = await session.exec(statement)
        user = execute.first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Sesssion error. credentials mismatch",
            )
        return user
