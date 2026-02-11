from http import HTTPStatus
from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Request
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.routers.auth import get_current_user
from app.schemas import MoviePublic, MovieSchema, MovieUpdate, movie_form, update_movie_form, new_poster
from app.models import Movie, User

router = APIRouter(prefix='/movies', tags=['movies'])

Session = Annotated[AsyncSession, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]
MovieFormSchema = Annotated[MovieSchema, Depends(movie_form)]
UpdateMovieFormSchema = Annotated[MovieSchema, Depends(update_movie_form)]


@router.post('/', status_code=HTTPStatus.CREATED, response_model=MoviePublic)
async def create_movie(
        movie: MovieFormSchema,
        session: Session,
        current_user: CurrentUser,
        request: Request,
        poster: UploadFile = File(...),
):
    movie_id = str(uuid4())

    poster_info = new_poster(poster, request, movie_id)


    db_movie = Movie(
        id=movie_id,
        title=movie.title,
        year=movie.year,
        genre=movie.genre,
        poster_path=poster_info['poster_path'],
        poster_url=poster_info['poster_url'], # FIXME
        user_id=current_user.id
    )

    try:
        session.add(db_movie)
        await session.commit()
        await session.refresh(db_movie)
        await session.refresh(current_user)

        return db_movie

    except IntegrityError:
        raise HTTPException(status_code=HTTPStatus.CONFLICT, detail='Movie already exists')


@router.get('/', response_model=list[MoviePublic])
async def get_movies(session: Session):
    return await session.scalars(
        select(Movie)
    )


@router.get('/{movie_id}', response_model=MoviePublic)
async def get_movie_by_id(movie_id: str, session: Session):
    db_movie = await session.scalar(
        select(Movie).where(
            Movie.id == movie_id
        )
    )

    if not db_movie:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Movie not found.')

    return db_movie


@router.get('/{movie_id}/poster', response_class=FileResponse)
async def get_movie_poster_by_movie_id(movie_id: str, session: Session):
    db_movie = await session.scalar(
        select(Movie).where(
            Movie.id == movie_id,
        )
    )

    if not db_movie:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Movie not found.')

    return db_movie.poster_path


@router.patch('/{movie_id}', response_model=MoviePublic)
async def update_movie(
        movie_id: str,
        movie: UpdateMovieFormSchema,
        session: Session,
        current_user: CurrentUser,
        request: Request,
        poster: UploadFile | None = File(None),
):
    db_movie = await session.scalar(select(Movie).where(
        Movie.id == movie_id,
        Movie.user_id == current_user.id
    )
    )

    if not db_movie:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Movie not found.')

    for key, value in movie.model_dump(exclude_none=True).items():
        setattr(db_movie, key, value)

    if poster:
        poster_info = new_poster(poster,request, movie_id)
        db_movie.poster_path = poster_info['poster_path']
        db_movie.poster_url = poster_info['poster_url']

    try:
        await session.commit()
        await session.refresh(db_movie)
        await session.refresh(current_user)

        return db_movie

    except IntegrityError:
        raise HTTPException(status_code=HTTPStatus.CONFLICT, detail='Movie already exists')


@router.delete('/{movie_id}', response_model=dict)
async def delete_movie(movie_id: str, session: Session, current_user: CurrentUser):
    db_movie = await session.scalar(select(Movie).where(
            Movie.id == movie_id,
            Movie.user_id  == current_user.id
                            )
    )

    if not db_movie:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Movie not found.')

    await session.delete(db_movie)
    await session.commit()
    await session.refresh(current_user)

    return {'msg' : 'Movie deleted'}

