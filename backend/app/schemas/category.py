from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class CategoryBase(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    
    name: str
    description: Optional[str] = None


class CategoryCreate(CategoryBase):
    model_config = ConfigDict(protected_namespaces=())
    pass


class CategoryUpdate(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    
    name: Optional[str] = None
    description: Optional[str] = None


class CategoryResponse(CategoryBase):
    model_config = ConfigDict(from_attributes=True, protected_namespaces=())
    
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None