# from streamlit import user

from fastapi import APIRouter, HTTPException
from database import SessionLocal

from db_model import User
from auth import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token
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

    access_token=create_access_token(

    {
        "user_id":user.username
    }

)

    refresh_token=create_refresh_token(

        {
            "user_id":user.username
        }

    )

    return{

            "access_token":access_token,

            "refresh_token":refresh_token,

            "token_type":"bearer",

            "username":user.username

        }
@router.post("/refresh")

async def refresh(req:LoginRequest):

    data=await req.json()

    token=data["refresh_token"]

    payload=decode_token(token)

    if not payload:

        raise HTTPException(

            401,

            "Invalid refresh token"

        )

    if payload["type"]!="refresh":

        raise HTTPException(

            401,

            "Invalid token type"

        )

    access=create_access_token(

        {

            "user_id":payload["user_id"]

        }

    )

    return{

        "access_token":access

    }