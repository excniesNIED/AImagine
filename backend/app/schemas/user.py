from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    
    username: str
    email: EmailStr


class UserCreate(UserBase):
    model_config = ConfigDict(protected_namespaces=())
    
    password: str


class UserUpdate(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None


class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True, protected_namespaces=())
    
    id: int
    role: str
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None