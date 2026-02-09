from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import uuid4

from app.database import get_session
from app.schemas import UserPublic, UserSchema, UserUpdate
from app.security import get_password_hash
from app.models import User

Session = Annotated[AsyncSession, Depends(get_session)]


router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserPublic)
async def create_user(user: UserSchema, session: Session):
    new_user = User(
        id = str(uuid4()),
        username = user.username,
        email = user.email,
        password = get_password_hash(user.password),
    )

    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)

    return new_user

@router.get("/", response_model=list[UserPublic])
async def get_users(session: Session):
    return await session.scalars(select(User))

@router.get("/{user_id}", response_model=UserPublic)
async def get_user(user_id: str, session: Session):
    return await session.scalar(select(User).where(User.id == user_id))

@router.patch("/{user_id}", response_model=UserPublic)
async def update_user(user_id: str, user: UserUpdate, session: Session):
    db_user = await session.scalar(select(User).where(User.id == user_id))

    for key,value in user.model_dump(exclude_none=True).items():
        setattr(db_user, key, value)

    await session.commit()
    await session.refresh(db_user)

    return db_user


@router.delete("/{user_id}", response_model=dict)
async def delete_user(user_id: str, session: Session):
    user = await session.scalar(select(User).where(User.id == user_id))
    await session.delete(user)
    await session.commit()

    return {'msg': 'user deleted'}