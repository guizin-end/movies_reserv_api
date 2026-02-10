from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from typing import Annotated
from http import HTTPStatus

import jwt
from jwt import encode, decode, DecodeError
from pwdlib import PasswordHash
from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi.security import OAuth2PasswordBearer

from app.settings import Settings
from app.database import get_session
from app.models import User


pwd_context = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl='auth/token', refreshUrl='auth/refresh_token'
)

Token = Annotated[str, Depends(oauth2_scheme)]
Session = Annotated[AsyncSession, Depends(get_session)]


def get_password_hash(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.now(tz=ZoneInfo('UTC')) + timedelta(
        minutes = Settings().ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, Settings().SECRET_KEY, Settings().ALGORITHM
    )

    return encoded_jwt


async def get_current_user(token: Token, session: Session):
    credentials_exception = HTTPException(
        status_code=HTTPStatus.UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'},
    )

    try:
        payload = jwt.decode(token, Settings().SECRET_KEY, Settings().ALGORITHM)

        username= payload.get("sub")
        if not username:
            raise credentials_exception

    except (jwt.ExpiredSignatureError,
            jwt.DecodeError,
            jwt.InvalidTokenError):
        raise credentials_exception

    user = await session.scalar(select(User).where(User.email == username))

    if not user:
        raise credentials_exception

    return user
