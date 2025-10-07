from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from typing import Dict, Any
from app.core.database import get_db
from app.api.deps import get_current_admin_user
from app.models import User, Image, Category, Tag, Model
from app.services.alist_service import alist_service

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
    return {
        "alist": {
            "url": alist_service.base_url,
            "username": alist_service.username,
            "upload_path": alist_service.upload_path,
            "configured": bool(alist_service.token or alist_service.username)
        }
    }


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