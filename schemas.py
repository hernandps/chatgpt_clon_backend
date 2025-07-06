from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from enum import Enum

class RoleEnum(str, Enum):
    free = "free"
    premium = "premium"

class UserCreate(BaseModel):
    email: str
    password: str
    role: Optional[RoleEnum] = RoleEnum.free


class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class MessageCreate(BaseModel):
    content: str

class MessageOut(BaseModel):
    id: int
    content: str
    timestamp: datetime

    class Config:
        orm_mode = True