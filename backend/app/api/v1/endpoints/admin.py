from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, case, or_
from typing import Dict, Any, List, Optional
from app.core.database import get_db
from app.api.deps import get_current_admin_user
from app.models import User, Image, Category, Tag, Model, VersionHistory
from app.services.alist_service import alist_service
from app.core.config_store import config_store
from pydantic import BaseModel
from app.schemas.image import ImageListResponse

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


# ------------------------------
# Admin: Images by association
# ------------------------------

class BulkReassignCategoryPayload(BaseModel):
    source_category_id: int
    target_category_id: int
    image_ids: Optional[List[int]] = None


class BulkReassignModelPayload(BaseModel):
    source_model_id: int
    target_model_id: int
    image_ids: Optional[List[int]] = None


class BulkTagImagesPayload(BaseModel):
    image_ids: List[int]


@router.get("/images", response_model=ImageListResponse)
async def admin_list_images(
    skip: int = 0,
    limit: int = 20,
    search: Optional[str] = None,
    category_id: Optional[int] = None,
    model_id: Optional[int] = None,
    tag_ids: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    query = db.query(Image).options(
        joinedload(Image.model),
        joinedload(Image.category),
        joinedload(Image.tags),
        joinedload(Image.parameters)
    )

    if search:
        query = query.filter(
            or_(
                Image.prompt.ilike(f"%{search}%"),
                Image.negative_prompt.ilike(f"%{search}%")
            )
        )

    if category_id:
        query = query.filter(Image.category_id == category_id)

    if model_id:
        query = query.filter(Image.model_id == model_id)

    if tag_ids:
        from app.models.tag import Tag as TagModel
        tag_id_list = [int(x) for x in tag_ids.split(',') if x.strip()]
        if tag_id_list:
            query = query.join(Image.tags).filter(TagModel.id.in_(tag_id_list)).distinct()

    total = query.count()
    images = query.order_by(Image.created_at.desc()).offset(skip).limit(limit).all()

    return ImageListResponse(items=images, total=total, page=(skip // limit) + 1, size=limit)


@router.get("/categories/{category_id}/images", response_model=ImageListResponse)
async def admin_list_images_by_category(
    category_id: int,
    skip: int = 0,
    limit: int = 20,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    return await admin_list_images(
        skip=skip,
        limit=limit,
        search=search,
        category_id=category_id,
        model_id=None,
        tag_ids=None,
        db=db,
        current_user=current_user
    )


@router.get("/models/{model_id}/images", response_model=ImageListResponse)
async def admin_list_images_by_model(
    model_id: int,
    skip: int = 0,
    limit: int = 20,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    return await admin_list_images(
        skip=skip,
        limit=limit,
        search=search,
        category_id=None,
        model_id=model_id,
        tag_ids=None,
        db=db,
        current_user=current_user
    )


@router.get("/tags/{tag_id}/images", response_model=ImageListResponse)
async def admin_list_images_by_tag(
    tag_id: int,
    skip: int = 0,
    limit: int = 20,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    return await admin_list_images(
        skip=skip,
        limit=limit,
        search=search,
        category_id=None,
        model_id=None,
        tag_ids=str(tag_id),
        db=db,
        current_user=current_user
    )


@router.post("/images/bulk/reassign-category")
async def admin_bulk_reassign_category(
    payload: BulkReassignCategoryPayload,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    source = db.query(Category).filter(Category.id == payload.source_category_id).first()
    target = db.query(Category).filter(Category.id == payload.target_category_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="Source category not found")
    if not target:
        raise HTTPException(status_code=404, detail="Target category not found")

    query = db.query(Image).filter(Image.category_id == payload.source_category_id)
    if payload.image_ids:
        query = query.filter(Image.id.in_(payload.image_ids))

    updated_count = query.update({"category_id": payload.target_category_id}, synchronize_session=False)
    db.commit()
    return {"updated": int(updated_count)}


@router.post("/images/bulk/reassign-model")
async def admin_bulk_reassign_model(
    payload: BulkReassignModelPayload,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    source = db.query(Model).filter(Model.id == payload.source_model_id).first()
    target = db.query(Model).filter(Model.id == payload.target_model_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="Source model not found")
    if not target:
        raise HTTPException(status_code=404, detail="Target model not found")

    query = db.query(Image).filter(Image.model_id == payload.source_model_id)
    if payload.image_ids:
        query = query.filter(Image.id.in_(payload.image_ids))

    updated_count = query.update({"model_id": payload.target_model_id}, synchronize_session=False)
    db.commit()
    return {"updated": int(updated_count)}


@router.post("/tags/{tag_id}/attach-images")
async def admin_attach_images_to_tag(
    tag_id: int,
    payload: BulkTagImagesPayload,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")

    images = db.query(Image).filter(Image.id.in_(payload.image_ids)).all()
    if not images:
        return {"attached": 0}

    attached = 0
    existing_ids = {img.id for img in tag.images}
    for img in images:
        if img.id not in existing_ids:
            tag.images.append(img)
            attached += 1
    db.commit()
    return {"attached": attached}


@router.post("/tags/{tag_id}/detach-images")
async def admin_detach_images_from_tag(
    tag_id: int,
    payload: BulkTagImagesPayload,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")

    images = db.query(Image).filter(Image.id.in_(payload.image_ids)).all()
    if not images:
        return {"detached": 0}

    detached = 0
    for img in images:
        if img in tag.images:
            tag.images.remove(img)
            detached += 1
    db.commit()
    return {"detached": detached}


@router.delete("/categories/{category_id}/images")
async def admin_delete_images_by_category(
    category_id: int,
    delete_from_alist: bool = False,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    images = db.query(Image).filter(Image.category_id == category_id).all()

    deleted = 0
    skipped_with_children = 0
    for image in images:
        has_children = db.query(Image).filter(Image.parent_image_id == image.id).count() > 0
        if has_children:
            skipped_with_children += 1
            continue
        if delete_from_alist:
            try:
                await alist_service.delete_file(image.file_path)
            except Exception:
                pass
        db.query(VersionHistory).filter(
            or_(
                VersionHistory.parent_image_id == image.id,
                VersionHistory.child_image_id == image.id
            )
        ).delete()
        db.delete(image)
        deleted += 1

    db.commit()
    return {"deleted": deleted, "skipped_with_children": skipped_with_children}


@router.delete("/models/{model_id}/images")
async def admin_delete_images_by_model(
    model_id: int,
    delete_from_alist: bool = False,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    images = db.query(Image).filter(Image.model_id == model_id).all()

    deleted = 0
    skipped_with_children = 0
    for image in images:
        has_children = db.query(Image).filter(Image.parent_image_id == image.id).count() > 0
        if has_children:
            skipped_with_children += 1
            continue
        if delete_from_alist:
            try:
                await alist_service.delete_file(image.file_path)
            except Exception:
                pass
        db.query(VersionHistory).filter(
            or_(
                VersionHistory.parent_image_id == image.id,
                VersionHistory.child_image_id == image.id
            )
        ).delete()
        db.delete(image)
        deleted += 1

    db.commit()
    return {"deleted": deleted, "skipped_with_children": skipped_with_children}


@router.delete("/tags/{tag_id}/images")
async def admin_delete_images_by_tag(
    tag_id: int,
    delete_from_alist: bool = False,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    from app.models.tag import Tag as TagModel
    tag = db.query(TagModel).filter(TagModel.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")

    images = list(tag.images)

    deleted = 0
    skipped_with_children = 0
    for image in images:
        has_children = db.query(Image).filter(Image.parent_image_id == image.id).count() > 0
        if has_children:
            skipped_with_children += 1
            continue
        if delete_from_alist:
            try:
                await alist_service.delete_file(image.file_path)
            except Exception:
                pass
        db.query(VersionHistory).filter(
            or_(
                VersionHistory.parent_image_id == image.id,
                VersionHistory.child_image_id == image.id
            )
        ).delete()
        db.delete(image)
        deleted += 1

    db.commit()
    return {"deleted": deleted, "skipped_with_children": skipped_with_children}