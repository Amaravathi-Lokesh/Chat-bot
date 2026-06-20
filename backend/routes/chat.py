from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from model.models import response
from services.services import Service

router = APIRouter()
service = Service()


@router.post("/chat/send", response_model=response)
async def root(
    user_id: str,
    chat_id: int,
    message: str,
    db: Session = Depends(get_db)
):

    ai_response = await service.process_message(
        user_id=user_id,
        chat_id=chat_id,
        content=message,
        db=db
    )

    # print("AI RESPONSE =", ai_response)
    # print(type(ai_response))

    return {
        "message": str(ai_response)
    }