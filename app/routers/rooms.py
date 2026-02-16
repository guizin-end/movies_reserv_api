from http import HTTPStatus
from typing import Annotated
from uuid import uuid4
from string import ascii_uppercase
import os

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Request
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_session
from app.routers.auth import get_current_user
from app.schemas import CinemaRoomCompact, CinemaRoomFull
from app.models import Movie, User, CinemaRoom, Seat


CurrentUser = Annotated[User, Depends(get_current_user)]
Session = Annotated[AsyncSession, Depends(get_session)]


router = APIRouter(prefix='/rooms', tags=['rooms'])


@router.post("/", response_model=CinemaRoomCompact, status_code=HTTPStatus.CREATED)
async def seed_cinema_room(cinema_room_name, rows: int, columns: int, session: Session, current_user: CurrentUser):
    cinema_room = CinemaRoom(
        id=str(uuid4()), name=cinema_room_name, total_seats=columns*rows, user_id=current_user.id
    )

    seats = []
    for row in range(0, rows):
        for column in range(1, columns+1):
            seat = Seat(
                id=str(uuid4()),
                cinema_room_id=cinema_room.id,
                row=ascii_uppercase[row],
                column=column,
                is_aisle=(row == 1 or row == rows+1),
                is_accessible=False,
                        )
            seats.append(seat)

    session.add(cinema_room)
    session.add_all(seats)
    await session.commit()
    await session.refresh(cinema_room)

    return cinema_room


@router.get("/", response_model=list[CinemaRoomCompact])
async def get_all_cinema_rooms(session: Session):
    return await session.scalars(select(CinemaRoom))


@router.get("/{cinema_room_id}", response_model=CinemaRoomFull)
async def get_cinema_room_by_id(session: Session, cinema_room_id: str):
    cinema_room = await session.scalar(
        select(CinemaRoom)
        .where(CinemaRoom.id == cinema_room_id)
    )

    return cinema_room


@router.delete("/{cinema_room_id}")
async def delete_cinema_room(session: Session, cinema_room_id: str, current_user: CurrentUser):
    cinema_room = await session.scalar(
        select(CinemaRoom).where(
            CinemaRoom.id == cinema_room_id,
            CinemaRoom.user_id == current_user.id
        ))

    await session.delete(cinema_room)
    await session.commit()

    return {'msg': 'Cinema room was deleted'}
