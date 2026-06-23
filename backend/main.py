# raise Exception("MAIN FILE REACHED")
# print("step-1")
from fastapi import FastAPI
# print("step-2")
from database import engine, Base
from db_model import Message, Chat,User,Document,DocumentChunk,ChatMemory,ActiveEntity,ResponseCache
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi import _rate_limit_exceeded_handler
# Create tables
print("MAIN.PY STARTED")
print("Importing DATABASE")
Base.metadata.create_all(bind=engine)

# FastAPI app
app = FastAPI(
    title="FastAPI Chatbot",
    version="1.0.0"
)
limiter = Limiter(
    key_func=get_remote_address
)

app.state.limiter = limiter

app.add_exception_handler(
    RateLimitExceeded,
    _rate_limit_exceeded_handler
)

app.add_middleware(
    SlowAPIMiddleware
)

# Import routers

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
from routes.chat import router as chat_router
from routes.chat_session import router as chat_session_router

# Register routers (ONLY ONCE)
# app.include_router(chat_router)
app.include_router(chat_session_router)
from routes.auth import router as auth_router
app.include_router(auth_router)
from routes.upload import router as upload_router
app.include_router(upload_router)
from redis_client import redis_client
print("Database imported")
print("roytes imported")
@app.get("/redis-test")
def redis_test():

    redis_client.set(
        "hello",
        "world"
    )

    value = redis_client.get(
        "hello"
    )

    return {
        "value": value
    }
from services.cache_service import CacheService

@app.get("/cache-test")
def cache_test():

    CacheService.set(
        "test",
        {"message": "hello"}
    )

    return CacheService.get("test")
