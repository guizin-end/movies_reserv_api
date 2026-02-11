from http import HTTPStatus
from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.models import User
from app.schemas import UserPublic, UserSchema, UserUpdate
from app.security import get_password_hash
from app.routers.auth import get_current_user

Session = Annotated[AsyncSession, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]

router = APIRouter(prefix='/users', tags=['users'])


@router.post('/', response_model=UserPublic, status_code=HTTPStatus.CREATED)
async def create_user(user: UserSchema, session: Session):
    new_user = User(
        id=str(uuid4()),
        username=user.username,
        email=user.email,
        password=get_password_hash(user.password),
    )
    try:
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)

        return new_user

    except IntegrityError:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT, detail='User already exists.'
        )


@router.get('/', response_model=list[UserPublic])
async def get_users(session: Session):
    return await session.scalars(select(User))


@router.get('/{user_id}', response_model=UserPublic)
async def get_user_by_id(user_id: str, session: Session):
    user = await session.scalar(select(User).where(User.id == user_id))

    if not user:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='User does not exist.'
        )

    return user


@router.patch('/{user_id}', response_model=UserPublic)
async def update_user(
        user_id: str, user: UserUpdate, session: Session, current_user: CurrentUser
):
    db_user = await session.scalar(
        select(User).where(User.id == user_id, User.id == current_user.id)
    )

    if not db_user:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='User does not exist.'
        )

    try:
        for key, value in user.model_dump(exclude_none=True).items():
            if key == 'password':
                setattr(db_user, key, get_password_hash(value))
            else:
                setattr(db_user, key, value)

        await session.commit()
        await session.refresh(db_user)

        return db_user

    except IntegrityError:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT, detail='User already exists.'
        )


@router.delete('/{user_id}', response_model=dict)
async def delete_user(user_id: str, session: Session, current_user: CurrentUser):
    db_user = await session.scalar(
        select(User).where(User.id == user_id)
    )

    if not db_user:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='User does not exist.'
        )

    await session.delete(db_user)
    await session.commit()

    return {'msg': 'user deleted'}
