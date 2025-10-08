from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from typing import Dict, Any
from app.core.database import get_db
from app.api.deps import get_current_admin_user
from app.models import User, Image, Category, Tag, Model
from app.services.alist_service import alist_service
from app.core.config_store import config_store
from pydantic import BaseModel

router = APIRouter()


@router.get("/dashboard")
async def admin_dashboard(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    # Get statistics
    stats = {
        "users": db.query(User).count(),
        "images": db.query(Image).count(),
        "categories": db.query(Category).count(),
        "tags": db.query(Tag).count(),
        "models": db.query(Model).count(),
    }
    
    # Get recent images
    recent_images = db.query(Image).order_by(Image.created_at.desc()).limit(5).all()
    
    # Get user statistics
    user_stats = db.query(
        func.count(User.id).label('total'),
        func.sum(case((User.role == 'admin', 1), else_=0)).label('admins')
    ).first()
    
    return {
        "stats": stats,
        "recent_images": recent_images,
        "user_stats": {
            "total": user_stats.total,
            "admins": user_stats.admins or 0,
            "regular_users": (user_stats.total or 0) - (user_stats.admins or 0)
        }
    }


@router.get("/settings")
async def get_settings(
    current_user = Depends(get_current_admin_user)
):
    # Read directly from TOML to avoid hiding persisted password/token
    stored = config_store.get_section("alist")
    url = (stored.get("url") or "").strip()
    username = (stored.get("username") or "").strip()
    upload_path = (stored.get("upload_path") or "/gallery").strip()
    has_token = bool((stored.get("token") or "").strip())
    has_password = isinstance(stored.get("password"), str) and stored.get("password") != ""
    return {
        "alist": {
            "url": url,
            "username": username,
            "upload_path": upload_path,
            "configured": has_token or (username and has_password),
            "has_token": has_token,
            "has_password": has_password
        }
    }


class AlistSettingsUpdate(BaseModel):
    url: str | None = None
    token: str | None = None
    username: str | None = None
    password: str | None = None
    upload_path: str | None = None


@router.post("/settings/alist")
async def update_alist_settings(
    payload: AlistSettingsUpdate,
    current_user = Depends(get_current_admin_user)
):
    # Persist to TOML config
    update_values = {}
    if payload.url is not None and payload.url.strip():
        update_values["url"] = payload.url.strip()
    if payload.token is not None and payload.token.strip():
        update_values["token"] = payload.token.strip()
    if payload.username is not None and payload.username.strip():
        update_values["username"] = payload.username.strip()
    if payload.password is not None and payload.password:
        update_values["password"] = payload.password
    if payload.upload_path is not None and payload.upload_path.strip():
        # Normalize to leading '/' and no trailing slash
        path = "/" + payload.upload_path.strip().strip("/")
        update_values["upload_path"] = path

    if update_values:
        config_store.update_section("alist", update_values)

    # Refresh running alist_service values from the store
    stored = config_store.get_section("alist")
    alist_service.refresh_from_store()

    return {"message": "Alist settings updated", "alist": stored}


@router.post("/settings/test-alist")
async def test_alist_connection(
    current_user = Depends(get_current_admin_user)
):
    try:
        is_connected = await alist_service.test_connection()
        return {
            "success": is_connected,
            "message": "Connection successful" if is_connected else "Connection failed"
        }
    except Exception as e:
        return {
            "success": False,
            "message": str(e)
        }


@router.get("/users")
async def get_users(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    users = db.query(User).offset(skip).limit(limit).all()
    total = db.query(User).count()
    
    return {
        "users": users,
        "total": total,
        "page": (skip // limit) + 1,
        "size": limit
    }


@router.put("/users/{user_id}/role")
async def update_user_role(
    user_id: int,
    role: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if role not in ["admin", "user"]:
        raise HTTPException(status_code=400, detail="Invalid role")
    
    user.role = role
    db.commit()
    
    return {"message": f"User role updated to {role}"}


@router.put("/users/{user_id}/status")
async def update_user_status(
    user_id: int,
    is_active: bool,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.id == current_user.id and not is_active:
        raise HTTPException(status_code=400, detail="Cannot deactivate yourself")
    
    user.is_active = is_active
    db.commit()
    
    return {"message": f"User {'activated' if is_active else 'deactivated'}"}