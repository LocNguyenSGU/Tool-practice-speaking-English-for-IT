from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    email: EmailStr
    username: str


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    username: str | None = None
    is_active: bool | None = None
    is_admin: bool | None = None


class UserInDB(UserBase):
    id: UUID
    is_active: bool
    is_admin: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class UserPublic(BaseModel):
    id: UUID
    email: EmailStr
    username: str
    is_admin: bool
    
    class Config:
        from_attributes = True
