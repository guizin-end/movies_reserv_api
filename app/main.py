import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request

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

@app.get('/url')
async def return_url(request: Request):
    # Get the full URL as a string
    full_url = str(request.url)

    # Get specific components
    domain = request.base_url
    path = request.url.path
    query_params = request.query_params

    return {
        "full_url": full_url,
        "domain": domain,
        "path": path,
        "query_params": query_params
    }