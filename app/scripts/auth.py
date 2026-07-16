from typing import Optional
from datetime import timedelta, datetime, timezone
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
