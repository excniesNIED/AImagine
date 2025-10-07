from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "AImagine"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = "sqlite:///./gallery.db"
    
    # Security
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Openlist/Alist
    ALIST_URL: Optional[str] = None
    ALIST_USERNAME: Optional[str] = None
    ALIST_PASSWORD: Optional[str] = None
    ALIST_TOKEN: Optional[str] = None
    ALIST_UPLOAD_PATH: str = "/gallery"
    
    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()