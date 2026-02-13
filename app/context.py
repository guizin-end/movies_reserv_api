from contextvars import ContextVar
from fastapi import Request


request_context: ContextVar[Request] = ContextVar("request_context")

async def request_middleware(request: Request, call_next):
    token = request_context.set(request)
    try:
        return await call_next(request)
    finally:
        request_context.reset(token)