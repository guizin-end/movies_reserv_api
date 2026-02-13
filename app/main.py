import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request

from app.routers import auth, movies, users
from app.context import request_context, request_middleware

logger = logging.getLogger('uvicorn.error')
logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app):
    logger.info('Starting application...')
    yield
    logger.info('Ending application...')


app = FastAPI(lifespan=lifespan)


app.include_router(auth.router)
app.include_router(movies.router)
app.include_router(users.router)
app.middleware("http")(request_middleware)


@app.get('/', response_model=dict)
async def root():
    return {'status': 'ok'}
