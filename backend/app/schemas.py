from pydantic import BaseModel, EmailStr

from app.models import UserRole


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: UserRole = UserRole.USER


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str