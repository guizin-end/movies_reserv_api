from pydantic import BaseModel, EmailStr, field_validator
from fastapi import Form, Request
from uuid import uuid4
from PIL import Image

from app.context import request_context
from app.models import SeatStatus


class UserSchema(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserPublic(BaseModel):
    id: str
    username: str
    email: EmailStr


class UserUpdate(BaseModel):
    username: str | None = None
    email: EmailStr | None = None
    password: str | None = None


class MovieSchema(BaseModel):
    title: str
    year: int
    genre: str


class MoviePublic(BaseModel):
    id: str
    title: str
    year: int
    genre: str
    poster_path: str
    poster_url: str

    @field_validator('poster_url', mode = 'after')
    @classmethod
    def serialize_url(cls, v):
        # Acessa o contexto passado na rota
        request = request_context.get()
        return f'{request.base_url}{v}'


class MovieUpdate(BaseModel):
    title: str | None = None
    year: int | None = None
    genre: str | None = None


class CinemaRoomCompact(BaseModel):
    id: str
    name: str
    total_seats: int


class Seat(BaseModel):
    row: str
    column: int
    is_aisle: bool
    is_accessible:bool
    seat_reservations.status: SeatStatus


class CinemaRoomFull(BaseModel):
    id: str
    name: str
    seats: list[Seat]


def movie_form(
        title: str = Form(...),
        year: int = Form(...),
        genre: str = Form(...),
):
    return MovieSchema(
        title=title,
        year=year,
        genre=genre
    )


def update_movie_form(
        title: str | None = Form(None),
        year: int | None = Form(None),
        genre: str | None = Form(None),
):
    return MovieUpdate(
        title=title if title and title != "string" and title.strip() else None,
        year=year if year and year != 0 else None,
        genre=genre if genre and genre != "string" and genre.strip() else None
    )


def new_poster(poster, request, movie_id):
    poster_id = str(uuid4())

    poster_info = {
        'poster_path' : f'./media/movies_posters/{poster_id}.png',
        'poster_url' : f'movies/{movie_id}/poster',
                    }

    db_poster = Image.open(poster.file)
    db_poster = db_poster.convert("RGB")
    db_poster.save(poster_info['poster_path'], optimize=True, quality=90, format="PNG")

    return poster_info
