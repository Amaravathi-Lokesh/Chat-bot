from fastapi import FastAPI
from database import engine, Base
from db_model import Message, Chat,User

# Create tables
Base.metadata.create_all(bind=engine)

# FastAPI app
app = FastAPI(
    title="FastAPI Chatbot",
    version="1.0.0"
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