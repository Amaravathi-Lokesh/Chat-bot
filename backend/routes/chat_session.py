from typing import List
from fastapi import APIRouter, Request,Depends
from sqlalchemy.orm import Session
from depends.rate_limit import enforce_rate_limit
from database import SessionLocal, get_db
from db_model import Chat, Message
from datetime import datetime
from model.models import (
    ChatCreateRequest,
    ChatListResponse,
    MessageResponse
)
from depends.limiter import limiter
from fastapi import Depends

from auth import get_current_user
from services.services import Service

router = APIRouter()

service = Service()


# ================= CREATE CHAT =================
@router.post("/chat/create")
async def create_chat(req: ChatCreateRequest):

    db = SessionLocal()

    chat = Chat(
        user_id=req.user_id,
        title=req.title
    )

    db.add(chat)
    db.commit()
    db.refresh(chat)
    db.close()

    return {
        "chat_id": chat.id,
        "title": chat.title
    }


# ================= LIST CHATS =================
@router.get("/chat/list/{user_id}", response_model=List[ChatListResponse])
async def list_chats(user_id: str):

    db = SessionLocal()

    try:
        chats = (
            db.query(Chat)
            .filter(Chat.user_id == user_id)
            .order_by(Chat.id.desc())
            .all()
        )

        return [
            ChatListResponse(
                id=chat.id,
                title=chat.title
            )
            for chat in chats
        ]

    finally:
        db.close()


# ================= CHAT HISTORY =================
@router.get("/chat/history/{chat_id}", response_model=List[MessageResponse])
async def get_chat_history(chat_id: int):

    db = SessionLocal()

    try:
        messages = (
            db.query(Message)
            .filter(Message.chat_id == chat_id)
            .order_by(Message.id.asc())
            .all()
        )

        return [
            MessageResponse(
                role=msg.role,
                content=msg.content
            )
            for msg in messages
        ]

    finally:
        db.close()


# ================= SEND MESSAGE (🔥 MAIN FIX) =================
@router.post("/chat/send")
@limiter.limit("10/minute")
async def send_message(request: Request,current_user=Depends(get_current_user)):
    enforce_rate_limit(current_user.id)
    data = await request.json()

    user_id = current_user.id
    chat_id = data["chat_id"]
    message = data["message"]

    db = SessionLocal()

    try:
        response = await service.process_message(
            user_id=user_id,
            chat_id=chat_id,
            content=message,
            db=db
        )

        # 🔥 FORCE STRING ALWAYS
        return {
            "message": str(response)
        }

    finally:
        db.close()
    router = APIRouter(prefix="/chat")

# ================= CREATE NEW CHAT =================
@router.post("/create")
def create_chat(user_id: str, title: str, db: Session = Depends(get_db)):
    new_chat = Chat(
        user_id=user_id,
        title=title,
        created_at=datetime.utcnow()
    )
    db.add(new_chat)
    db.commit()
    db.refresh(new_chat)

    return {
        "id": new_chat.id,
        "title": new_chat.title
    }

# ================= DELETE CHAT =================
@router.delete("/chat/delete/{chat_id}")
def delete_chat(chat_id: int, db: Session = Depends(get_db)):
    chat = db.query(Chat).filter(Chat.id == chat_id).first()

    if not chat:
        return {"error": "Chat not found"}

    db.delete(chat)
    db.commit()

    return {"message": "Chat deleted"}
@router.put("/chat/rename/{chat_id}")
async def rename_chat(
    chat_id: int,
    title: str,
    db: Session = Depends(get_db)
):

    chat = (
        db.query(Chat)
        .filter(Chat.id == chat_id)
        .first()
    )

    if not chat:
        return {"error": "Chat not found"}

    chat.title = title

    db.commit()

    return {
        "success": True,
        "title": title
    }
from fastapi.responses import StreamingResponse

@router.post("/chat/stream")
async def stream_chat(req: Request):

    data = await req.json()
    db = SessionLocal()
    return StreamingResponse(
        service.stream_message(
            user_id=data["user_id"],
            chat_id=data["chat_id"],
            content=data["message"],
            db=db
        ),
        media_type="text/event-stream"
    )