from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, and_
from typing import List, Optional
from app.core.database import get_db
from app.api.deps import get_current_active_user, get_current_admin_user, get_current_user_optional
from app.models import Image, User, Tag, KeyValueParameter, VersionHistory
import json
from app.schemas.image import ImageCreate, ImageUpdate, ImageResponse, ImageListResponse
from app.services.alist_service import alist_service
import uuid
import os

router = APIRouter()


@router.get("/public", response_model=ImageListResponse)
async def get_public_images(
    skip: int = 0,
    limit: int = 20,
    search: Optional[str] = None,
    category_id: Optional[int] = None,
    model_id: Optional[int] = None,
    # Multi-select support
    category_ids: Optional[str] = None,
    model_ids: Optional[str] = None,
    # Custom selections support
    custom_category: Optional[str] = None,
    custom_model: Optional[str] = None,
    custom_categories: Optional[str] = None,
    custom_models: Optional[str] = None,
    # Tag filter
    tag_ids: Optional[str] = None,
    # Parameter filters: provide either comma-separated keys or JSON mapping of key->value
    param_keys: Optional[str] = None,
    param_filters: Optional[str] = None,
    # Visibility policy hints
    enforce_visibility: bool = False,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """Get all public images for the gallery/square page"""
    query = db.query(Image).options(
        joinedload(Image.model),
        joinedload(Image.category),
        joinedload(Image.tags),
        joinedload(Image.parameters)
    ).filter(Image.is_public == True)
    
    # Search filter
    if search:
        query = query.filter(
            or_(
                Image.prompt.ilike(f"%{search}%"),
                Image.negative_prompt.ilike(f"%{search}%")
            )
        )
    
    # Category filter (single and multi)
    if category_id:
        query = query.filter(Image.category_id == category_id)
    if category_ids:
        try:
            ids = [int(x) for x in category_ids.split(',') if x.strip()]
            if ids:
                query = query.filter(Image.category_id.in_(ids))
        except Exception:
            pass
    # Custom category (single and multi)
    if custom_category:
        query = query.filter(Image.custom_category == custom_category)
    if custom_categories:
        custom_list = [x.strip() for x in custom_categories.split(',') if x.strip()]
        if custom_list:
            query = query.filter(Image.custom_category.in_(custom_list))
    
    # Model filter (single and multi)
    if model_id:
        query = query.filter(Image.model_id == model_id)
    if model_ids:
        try:
            ids = [int(x) for x in model_ids.split(',') if x.strip()]
            if ids:
                query = query.filter(Image.model_id.in_(ids))
        except Exception:
            pass
    # Custom model (single and multi)
    if custom_model:
        query = query.filter(Image.custom_model == custom_model)
    if custom_models:
        custom_list = [x.strip() for x in custom_models.split(',') if x.strip()]
        if custom_list:
            query = query.filter(Image.custom_model.in_(custom_list))
    
    # Tags filter (already supports multi via CSV)
    if tag_ids:
        tag_id_list = [int(x) for x in tag_ids.split(',') if x.strip()]
        if tag_id_list:
            query = query.join(Image.tags).filter(Tag.id.in_(tag_id_list)).distinct()

    # Parameter filters
    # - param_keys: comma-separated keys that must be present on the image (any value)
    # - param_filters: JSON string mapping key -> exact value (all key-value pairs must match)
    if param_keys:
        keys = [k.strip() for k in param_keys.split(',') if k.strip()]
        for k in keys:
            query = query.filter(Image.parameters.any(KeyValueParameter.key == k))
    if param_filters:
        try:
            kv = json.loads(param_filters)
            if isinstance(kv, dict):
                for k, v in kv.items():
                    if v is None or str(v).strip() == "":
                        # Only require key presence
                        query = query.filter(Image.parameters.any(KeyValueParameter.key == k))
                    else:
                        query = query.filter(
                            Image.parameters.any(
                                and_(KeyValueParameter.key == k, KeyValueParameter.value == str(v))
                            )
                        )
        except Exception:
            pass

    # Enforce visibility: if requested, restrict images that contain private tags
    if enforce_visibility:
        if current_user is None:
            # Anonymous viewers should not see images having any private tag
            query = query.filter(~Image.tags.any(Tag.is_public == False))
        else:
            # Admin can see all; regular users cannot see images with private tags owned by others
            if getattr(current_user, "role", None) and getattr(current_user.role, "value", None) == "admin":
                pass
            else:
                query = query.filter(
                    ~Image.tags.any(and_(Tag.is_public == False, Tag.owner_id != current_user.id))
                )
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    images = query.order_by(Image.created_at.desc()).offset(skip).limit(limit).all()
    
    return ImageListResponse(
        items=images,
        total=total,
        page=(skip // limit) + 1,
        size=limit
    )


@router.get("/", response_model=ImageListResponse)
async def get_images(
    skip: int = 0,
    limit: int = 20,
    search: Optional[str] = None,
    category_id: Optional[int] = None,
    model_id: Optional[int] = None,
    # Multi-select support
    category_ids: Optional[str] = None,
    model_ids: Optional[str] = None,
    # Custom selections support
    custom_category: Optional[str] = None,
    custom_model: Optional[str] = None,
    custom_categories: Optional[str] = None,
    custom_models: Optional[str] = None,
    # Tag filter
    tag_ids: Optional[str] = None,
    # Parameter filters
    param_keys: Optional[str] = None,
    param_filters: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    query = db.query(Image).options(
        joinedload(Image.model),
        joinedload(Image.category),
        joinedload(Image.tags),
        joinedload(Image.parameters)
    )
    
    # Non-admin users can only see their own images
    if current_user.role.value != "admin":
        query = query.filter(Image.owner_id == current_user.id)
    
    # Search filter
    if search:
        query = query.filter(
            or_(
                Image.prompt.ilike(f"%{search}%"),
                Image.negative_prompt.ilike(f"%{search}%")
            )
        )
    
    # Category filter (single and multi)
    if category_id:
        query = query.filter(Image.category_id == category_id)
    if category_ids:
        try:
            ids = [int(x) for x in category_ids.split(',') if x.strip()]
            if ids:
                query = query.filter(Image.category_id.in_(ids))
        except Exception:
            pass
    # Custom category (single and multi)
    if custom_category:
        query = query.filter(Image.custom_category == custom_category)
    if custom_categories:
        custom_list = [x.strip() for x in custom_categories.split(',') if x.strip()]
        if custom_list:
            query = query.filter(Image.custom_category.in_(custom_list))
    
    # Model filter (single and multi)
    if model_id:
        query = query.filter(Image.model_id == model_id)
    if model_ids:
        try:
            ids = [int(x) for x in model_ids.split(',') if x.strip()]
            if ids:
                query = query.filter(Image.model_id.in_(ids))
        except Exception:
            pass
    # Custom model (single and multi)
    if custom_model:
        query = query.filter(Image.custom_model == custom_model)
    if custom_models:
        custom_list = [x.strip() for x in custom_models.split(',') if x.strip()]
        if custom_list:
            query = query.filter(Image.custom_model.in_(custom_list))
    
    # Tags filter (already supports multi via CSV)
    if tag_ids:
        tag_id_list = [int(x) for x in tag_ids.split(',') if x.strip()]
        if tag_id_list:
            query = query.join(Image.tags).filter(Tag.id.in_(tag_id_list)).distinct()

    # Parameter filters
    if param_keys:
        keys = [k.strip() for k in param_keys.split(',') if k.strip()]
        for k in keys:
            query = query.filter(Image.parameters.any(KeyValueParameter.key == k))
    if param_filters:
        try:
            kv = json.loads(param_filters)
            if isinstance(kv, dict):
                for k, v in kv.items():
                    if v is None or str(v).strip() == "":
                        query = query.filter(Image.parameters.any(KeyValueParameter.key == k))
                    else:
                        query = query.filter(
                            Image.parameters.any(
                                and_(KeyValueParameter.key == k, KeyValueParameter.value == str(v))
                            )
                        )
        except Exception:
            pass
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    images = query.order_by(Image.created_at.desc()).offset(skip).limit(limit).all()
    
    return ImageListResponse(
        items=images,
        total=total,
        page=(skip // limit) + 1,
        size=limit
    )


@router.post("/", response_model=ImageResponse)
async def upload_image(
    file: UploadFile = File(...),
    prompt: str = Form(...),
    negative_prompt: Optional[str] = Form(None),
    model_id: Optional[int] = Form(None),
    category_id: Optional[int] = Form(None),
    custom_model: Optional[str] = Form(None),
    custom_category: Optional[str] = Form(None),
    is_public: bool = Form(False),
    tag_ids: Optional[str] = Form(None),
    parameters: Optional[str] = Form(None),
    parent_image_id: Optional[int] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Validate file type
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only image files are allowed"
        )
    
    # Validate that either model_id or custom_model is provided
    if not model_id and not custom_model:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either model_id or custom_model must be provided"
        )
    
    # Validate that either category_id or custom_category is provided
    if not category_id and not custom_category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either category_id or custom_category must be provided"
        )
    
    # Generate unique filename
    file_ext = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_ext}"

    # Get image dimensions BEFORE uploading (to avoid exhausted stream)
    width = None
    height = None
    try:
        from PIL import Image as PILImage
        import io
        image_data = await file.read()
        img = PILImage.open(io.BytesIO(image_data))
        width, height = img.size
        await file.seek(0)  # Reset file pointer for upload
    except Exception:
        pass

    # Upload to Alist
    try:
        print(
            f"[Upload] user={current_user.id} filename={unique_filename} size_hint={getattr(file, 'size', 'n/a')} upload_path_hint={getattr(alist_service, 'upload_path', 'n/a')}"
        )
        upload_result = await alist_service.upload_file(
            file=file,
            filename=unique_filename,
            subfolder=str(current_user.id)
        )
    except Exception as e:
        print(f"[Upload] alist error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload file: {str(e)}"
        )

    # Parse parameters
    params_list = []
    if parameters:
        try:
            import json
            params_data = json.loads(parameters)
            for key, value in params_data.items():
                params_list.append(KeyValueParameter(key=key, value=str(value)))
        except:
            pass
    
    # Parse tags
    tag_ids_list = []
    if tag_ids:
        tag_ids_list = [int(x) for x in tag_ids.split(',') if x.strip()]
    
    # Create image record
    db_image = Image(
        prompt=prompt,
        negative_prompt=negative_prompt,
        alist_url=upload_result["url"],
        file_path=upload_result["file_path"],
        file_name=unique_filename,
        file_size=upload_result["size"],
        width=width,
        height=height,
        is_public=is_public,
        custom_model=custom_model,
        custom_category=custom_category,
        owner_id=current_user.id,
        model_id=model_id,
        category_id=category_id,
        parent_image_id=parent_image_id,
        parameters=params_list
    )
    
    db.add(db_image)
    db.commit()
    db.refresh(db_image)
    
    # Add tags
    if tag_ids_list:
        tags = db.query(Tag).filter(Tag.id.in_(tag_ids_list)).all()
        db_image.tags.extend(tags)
        db.commit()
    
    # Create version history if parent image exists
    if parent_image_id:
        version = VersionHistory(
            parent_image_id=parent_image_id,
            child_image_id=db_image.id
        )
        db.add(version)
        db.commit()
    
    # Reload with relationships
    db_image = db.query(Image).options(
        joinedload(Image.model),
        joinedload(Image.category),
        joinedload(Image.tags),
        joinedload(Image.parameters)
    ).filter(Image.id == db_image.id).first()
    
    return db_image


@router.get("/{image_id}", response_model=ImageResponse)
async def get_image(
    image_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    image = db.query(Image).options(
        joinedload(Image.model),
        joinedload(Image.category),
        joinedload(Image.tags),
        joinedload(Image.parameters)
    ).filter(Image.id == image_id).first()
    
    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found"
        )
    
    # Check permissions
    if current_user.role.value != "admin" and image.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this image"
        )
    
    return image


@router.put("/{image_id}", response_model=ImageResponse)
async def update_image(
    image_id: int,
    image_update: ImageUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    image = db.query(Image).filter(Image.id == image_id).first()
    
    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found"
        )
    
    # Check permissions
    if current_user.role.value != "admin" and image.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this image"
        )
    
    # Update fields
    update_data = image_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field == "tags" and value is not None:
            # Update tags
            image.tags.clear()
            tags = db.query(Tag).filter(Tag.id.in_(value)).all()
            image.tags.extend(tags)
        elif field == "parameters" and value is not None:
            # Update parameters
            image.parameters.clear()
            for param in value:
                image.parameters.append(KeyValueParameter(**param.model_dump()))
        else:
            setattr(image, field, value)
    
    db.commit()
    db.refresh(image)
    
    # Reload with relationships
    image = db.query(Image).options(
        joinedload(Image.model),
        joinedload(Image.category),
        joinedload(Image.tags),
        joinedload(Image.parameters)
    ).filter(Image.id == image_id).first()
    
    return image


@router.get("/{image_id}/versions", response_model=List[ImageResponse])
async def get_image_versions(
    image_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Check if image exists and user has access
    image = db.query(Image).filter(Image.id == image_id).first()

    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found"
        )

    if current_user.role.value != "admin" and image.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this image"
        )

    # Get all versions - find all related images
    # First, find the root image (if this has a parent, follow up)
    root_id = image_id
    while image.parent_image_id:
        root_id = image.parent_image_id
        image = db.query(Image).filter(Image.id == root_id).first()

    # Now find all children of the root
    all_versions = db.query(Image).options(
        joinedload(Image.model),
        joinedload(Image.category),
        joinedload(Image.tags),
        joinedload(Image.parameters)
    ).filter(
        or_(
            Image.id == root_id,
            Image.parent_image_id == root_id
        )
    ).order_by(Image.created_at.asc()).all()

    # Recursively find all descendants
    def find_all_versions(parent_id: int, versions: List[Image]):
        children = db.query(Image).options(
            joinedload(Image.model),
            joinedload(Image.category),
            joinedload(Image.tags),
            joinedload(Image.parameters)
        ).filter(Image.parent_image_id == parent_id).all()

        for child in children:
            versions.append(child)
            find_all_versions(child.id, versions)

    versions = []
    # Add root image first
    root_image = db.query(Image).options(
        joinedload(Image.model),
        joinedload(Image.category),
        joinedload(Image.tags),
        joinedload(Image.parameters)
    ).filter(Image.id == root_id).first()

    if root_image:
        versions.append(root_image)
        find_all_versions(root_id, versions)

    return versions


@router.post("/{image_id}/iterate", response_model=ImageResponse)
async def create_new_version(
    image_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Get the parent image
    parent_image = db.query(Image).filter(Image.id == image_id).first()

    if not parent_image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found"
        )

    # Check permissions
    if current_user.role.value != "admin" and parent_image.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this image"
        )

    # Return parent image data for pre-filling the upload form
    return parent_image


@router.delete("/{image_id}")
async def delete_image(
    image_id: int,
    delete_from_alist: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    image = db.query(Image).filter(Image.id == image_id).first()

    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found"
        )

    # Check permissions
    if current_user.role.value != "admin" and image.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this image"
        )

    # Check if this image has children
    has_children = db.query(Image).filter(Image.parent_image_id == image_id).count() > 0

    if has_children:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete image that has child versions. Delete child versions first."
        )

    # Delete from Alist if requested
    if delete_from_alist:
        try:
            await alist_service.delete_file(image.file_path)
        except Exception as e:
            print(f"Failed to delete file from Alist: {e}")

    # Delete version history entries
    db.query(VersionHistory).filter(
        or_(
            VersionHistory.parent_image_id == image_id,
            VersionHistory.child_image_id == image_id
        )
    ).delete()

    # Delete from database
    db.delete(image)
    db.commit()

    return {"message": "Image deleted successfully"}