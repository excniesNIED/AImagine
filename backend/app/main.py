from pydantic import BaseModel, ConfigDict
# Silence Pydantic warnings for fields starting with "model_" (e.g., model_id)
BaseModel.model_config = ConfigDict(protected_namespaces=())

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.api import api_router
from app.core.database import Base, engine
from app.utils.init_db import init_db
# Import all models to register them with SQLAlchemy
from app.models import User, Image, Category, Tag, Model, VersionHistory, KeyValueParameter

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

@app.on_event("startup")
async def startup_event():
    # Create all database tables
    Base.metadata.create_all(bind=engine)
    # Initialize default data
    init_db()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4321", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    return {"message": "AImagine API", "version": settings.VERSION}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}