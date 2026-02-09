import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.routers import auth, movies, users

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


@app.get('/', response_model=dict)
async def root():
    return {'status': 'ok'}
