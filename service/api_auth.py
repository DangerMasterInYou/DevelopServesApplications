from enum import Enum
from fastapi import Request, HTTPException
from sqlalchemy import select
from passlib.hash import sha256_crypt
from datetime import datetime, timedelta, timezone
from typing import Optional
from database.connect import SessionDep
from database.models.base import TokenModel
import jwt
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")


class TokenType(Enum):
    access = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "0"))
    refresh = int(os.getenv("REFRESH_TOKEN_EXPIRE_MINUTES", "0"))


def create_jwt_token(data: dict, expires_delta_minutes: int):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=expires_delta_minutes)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def hash_password(password: str) -> str:
    return sha256_crypt.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return sha256_crypt.verify(plain_password, hashed_password)


async def jwt_checker(request: Request, session: SessionDep) -> Optional[str]:
    access_token: Optional[str] = request.cookies.get("access_token")
    if not access_token:
        raise HTTPException(status_code=403, detail="Access token missing")

    try:
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("exp") < datetime.now(timezone.utc).timestamp():
            raise HTTPException(status_code=403, detail="Access token expired")
        query = await session.execute(
            select(TokenModel).filter(TokenModel.access_token == access_token)
        )
        token_in_db = query.scalar_one_or_none()

        if token_in_db:
            return payload
        raise HTTPException(status_code=403, detail="Access token not found in database")

    except jwt.PyJWTError:
        raise HTTPException(status_code=403, detail="Invalid access token")
