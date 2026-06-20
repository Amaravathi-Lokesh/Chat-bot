from pydantic import BaseModel
class request(BaseModel):
    user_id: str
    chat_id: str
    message: str

class response(BaseModel):
    # user_id: str | None
    message: str
class ChatCreateRequest(BaseModel):
    user_id: str
    title: str

class ChatCreateResponse(BaseModel):
    chat_id: int
    title: str
class ChatListResponse(BaseModel):
    id: int
    title: str
class MessageResponse(BaseModel):
    role: str
    content: str
class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str
class ChatRequest(BaseModel):
    user_id: str
    chat_id: int
    message: str

class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    username: str