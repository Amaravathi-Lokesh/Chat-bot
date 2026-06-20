from jose import jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from database import SessionLocal
from db_model import User
from config.settings import Settings
SECRET_KEY = Settings.key
ALGORITHM = "HS256"
Refresh_token=7
Access_token=3
security=HTTPBearer()
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

def hash_password(password):
    return pwd_context.hash(password)

def verify_password(password, hashed):
    return pwd_context.verify(password, hashed)

def create_refresh_token(data: dict):

    payload = data.copy()

    payload["exp"] = (
        datetime.utcnow()
        + timedelta(days=Refresh_token)
    )

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )
def create_access_token(data):

    payload=data.copy()

    payload["type"]="access"

    payload["exp"]=datetime.utcnow()+timedelta(
        days=Access_token
    )

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )
from jose import JWTError

def decode_token(token):

    try:

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        return payload

    except JWTError as e:
        print(e)
        return None
# def get_current_user(

#     credentials: HTTPAuthorizationCredentials = Depends(security)

# ):

#     token = credentials.credentials

#     payload = decode_token(token)

#     if payload is None:

#         raise HTTPException(

#             status_code=401,

#             detail="Invalid Token"

#         )

#     id= payload.get("user_id")

#     db = SessionLocal()

#     user = (

#         db.query(User)

#         .filter(

#             User.id == int(id)

#         )

#         .first()

#     )

#     if user is None:

#         raise HTTPException(

#             status_code=401,

#             detail="User not found"

#         )

#     return user
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):

    token = credentials.credentials

    print("TOKEN:")
    print(token)

    payload = decode_token(token)

    print("PAYLOAD:")
    print(payload)

    if payload is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid Token"
        )

    user_id = payload.get("user_id")

    # print("USER ID:")
    # print(user_id)
    # print(type(user_id))

    db = SessionLocal()

    user = (
        db.query(User)
        .filter(
            User.id == int(user_id)
        )
        .first()
    )

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="User not found"
        )

    return user