from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class ModelBase(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    
    name: str
    description: Optional[str] = None


class ModelCreate(ModelBase):
    model_config = ConfigDict(protected_namespaces=())
    pass


class ModelUpdate(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    
    name: Optional[str] = None
    description: Optional[str] = None


class ModelResponse(ModelBase):
    model_config = ConfigDict(from_attributes=True, protected_namespaces=())
    
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    image_count: Optional[int] = None