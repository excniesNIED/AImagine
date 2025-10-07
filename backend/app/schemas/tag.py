from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class TagBase(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    
    name: str
    description: Optional[str] = None
    is_public: Optional[bool] = True


class TagCreate(TagBase):
    model_config = ConfigDict(protected_namespaces=())
    pass


class TagUpdate(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    
    name: Optional[str] = None
    description: Optional[str] = None
    is_public: Optional[bool] = None


class TagResponse(TagBase):
    model_config = ConfigDict(from_attributes=True, protected_namespaces=())
    
    id: int
    owner_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    image_count: Optional[int] = None