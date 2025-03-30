from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID
from datetime import datetime


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: Optional[str] = None


class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    yandex_id: str


class UserUpdate(BaseModel):
    full_name: Optional[str] = None


class UserOut(UserBase):
    id: UUID
    is_superuser: bool

    class Config:
        orm_mode = True


class AudioFileBase(BaseModel):
    file_name: str


class AudioFileCreate(AudioFileBase):
    pass


class AudioFileOut(AudioFileBase):
    id: UUID
    file_path: str
    created_at: datetime

    class Config:
        orm_mode = True
