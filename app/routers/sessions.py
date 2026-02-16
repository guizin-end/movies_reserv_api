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


from app.database import get_session
from app.routers.auth import get_current_user
from app.schemas import MoviePublic, MovieSchema, MovieUpdate, movie_form, update_movie_form, new_poster
from app.models import Movie, User, CinemaRoom, Seat


CurrentUser = Annotated[User, Depends(get_current_user)]
Session = Annotated[AsyncSession, Depends(get_session)]


router = APIRouter(prefix='/sessions', tags=['sessions'])

