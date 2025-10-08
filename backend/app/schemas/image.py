from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime
from .model import ModelResponse
from .category import CategoryResponse
from .tag import TagResponse


class KeyValueParameterBase(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    
    key: str
    value: Optional[str] = None


class KeyValueParameterCreate(KeyValueParameterBase):
    model_config = ConfigDict(protected_namespaces=())
    pass


class ImageBase(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    
    prompt: str
    negative_prompt: Optional[str] = None
    model_id: Optional[int] = None
    category_id: Optional[int] = None
    custom_model: Optional[str] = None
    custom_category: Optional[str] = None
    is_public: bool = False
    tags: List[int] = []
    parameters: List[KeyValueParameterCreate] = []


class ImageCreate(ImageBase):
    model_config = ConfigDict(protected_namespaces=())
    
    file_name: str
    file_size: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None
    parent_image_id: Optional[int] = None


class ImageUpdate(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    
    prompt: Optional[str] = None
    negative_prompt: Optional[str] = None
    model_id: Optional[int] = None
    category_id: Optional[int] = None
    custom_model: Optional[str] = None
    custom_category: Optional[str] = None
    is_public: Optional[bool] = None
    tags: Optional[List[int]] = None
    parameters: Optional[List[KeyValueParameterCreate]] = None


class KeyValueParameterResponse(KeyValueParameterBase):
    model_config = ConfigDict(from_attributes=True, protected_namespaces=())
    
    id: int
    created_at: datetime


class ImageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, protected_namespaces=())
    
    id: int
    prompt: str
    negative_prompt: Optional[str] = None
    alist_url: str
    file_path: str
    file_name: str
    file_size: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None
    is_public: bool = False
    custom_model: Optional[str] = None
    custom_category: Optional[str] = None
    owner_id: int
    model_id: Optional[int] = None
    category_id: Optional[int] = None
    parent_image_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Nested relationships
    model: Optional[ModelResponse] = None
    category: Optional[CategoryResponse] = None
    tags: List[TagResponse] = []
    parameters: List[KeyValueParameterResponse] = []


class ImageListResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    
    items: List[ImageResponse]
    total: int
    page: int
    size: int