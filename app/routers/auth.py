from typing import Annotated
from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_

from app.security import get_current_user, verify_password, create_access_token
from app.database import get_session
from app.models import User


Session = Annotated[AsyncSession, Depends(get_session)]
AuthForm = Annotated[OAuth2PasswordRequestForm, Depends()]
CurrentUser = Annotated[User, Depends(get_current_user)]
router = APIRouter(prefix='/auth', tags=['auth'])


@router.post('/token')
async def login_for_access_token(form_data: AuthForm, session: Session):
    db_user = await session.scalar(
        select(User).where(
            or_(
                User.email == form_data.username,
                User.username == form_data.username
            )
        )
    )

    if not db_user:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="This user does not exist.")

    if not verify_password(form_data.password, db_user.password):
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="Incorrect password.")

    return {
        'access_token': create_access_token(data={'sub': db_user.email}),
        'token_type': 'bearer',
    }
