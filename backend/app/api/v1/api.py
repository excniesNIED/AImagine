from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, images, categories, tags, models, admin

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(images.router, prefix="/images", tags=["images"])
api_router.include_router(categories.router, prefix="/categories", tags=["categories"])
api_router.include_router(tags.router, prefix="/tags", tags=["tags"])
api_router.include_router(models.router, prefix="/models", tags=["models"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])