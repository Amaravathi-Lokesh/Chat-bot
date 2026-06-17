# from streamlit import user

from fastapi import APIRouter, HTTPException
from database import SessionLocal

from db_model import User
from auth import (
    hash_password,
    verify_password,
    create_token
)

from model.models import (
    RegisterRequest,
    LoginRequest
)

router = APIRouter(prefix="/auth")


@router.post("/register")
async def register(req: RegisterRequest):

    db = SessionLocal()

    existing = (
        db.query(User)
        .filter(
            User.username == req.username
        )
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Username already exists"
        )

    user = User(
        username=req.username,
        email=req.email,
        password=hash_password(
            req.password
        )
    )

    db.add(user)
    db.commit()

    return {
        "message": "User created"
    }


@router.post("/login")
async def login(req: LoginRequest):

    db = SessionLocal()

    user = (
        db.query(User)
        .filter(User.username == req.username)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    if not verify_password(
        req.password,
        user.password
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    token = create_token(
            {
                "user_id": str(user.id)
            }
        )

    response = {
            "access_token": token,
            "token_type":"Bearer",
            "username": user.username
        }

        # print("LOGIN RESPONSE:")
        # print(response)

    return response