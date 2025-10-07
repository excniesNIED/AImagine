from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from typing import List, Optional
from app.core.database import get_db
from app.api.deps import get_current_active_user, get_current_admin_user, get_current_user_optional
from app.models.tag import Tag, image_tags
from app.models.user import User
from app.schemas.tag import TagCreate, TagUpdate, TagResponse

router = APIRouter()


@router.get("/", response_model=List[TagResponse])
async def get_tags(
    skip: int = 0,
    limit: int = 100,
    include_count: bool = False,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    # Return tags that are either:
    # 1. Public (is_public=True)
    # 2. Owned by the current user (if logged in)
    # 3. Admin-created (owner_id is None)
    if current_user:
        query = db.query(Tag).filter(
            or_(
                Tag.is_public == True,
                Tag.owner_id == current_user.id,
                Tag.owner_id == None
            )
        )
    else:
        # For anonymous users, only show public tags and admin-created tags
        query = db.query(Tag).filter(
            or_(
                Tag.is_public == True,
                Tag.owner_id == None
            )
        )
    
    if include_count:
        # Add image count to each tag
        query = query.outerjoin(image_tags).group_by(Tag.id)
        query = query.add_columns(func.count(image_tags.c.image_id).label('image_count'))
        results = query.offset(skip).limit(limit).all()
        
        tags = []
        for tag, count in results:
            tag_dict = TagResponse.model_validate(tag)
            tag_dict.image_count = count
            tags.append(tag_dict)
        return tags
    else:
        tags = query.offset(skip).limit(limit).all()
        return tags


@router.post("/", response_model=TagResponse)
async def create_tag(
    tag: TagCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Check if tag already exists for this user or as admin tag
    existing = db.query(Tag).filter(
        Tag.name == tag.name,
        or_(
            Tag.owner_id == current_user.id,
            Tag.owner_id == None
        )
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tag already exists"
        )
    
    tag_data = tag.model_dump()
    tag_data['owner_id'] = current_user.id
    db_tag = Tag(**tag_data)
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)
    
    return db_tag


@router.put("/{tag_id}", response_model=TagResponse)
async def update_tag(
    tag_id: int,
    tag_update: TagUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found"
        )
    
    # Check if user has permission to update this tag
    from app.models.user import UserRole
    if tag.owner_id != current_user.id and current_user.role != UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this tag"
        )
    
    # Check if new name conflicts with existing tag
    if tag_update.name and tag_update.name != tag.name:
        existing = db.query(Tag).filter(
            Tag.name == tag_update.name,
            or_(
                Tag.owner_id == current_user.id,
                Tag.owner_id == None
            )
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tag name already exists"
            )
    
    update_data = tag_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(tag, field, value)
    
    db.commit()
    db.refresh(tag)
    
    return tag


@router.delete("/{tag_id}")
async def delete_tag(
    tag_id: int,
    merge_into_id: int = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found"
        )
    
    # Check if user has permission to delete this tag
    from app.models.user import UserRole
    if tag.owner_id != current_user.id and current_user.role != UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this tag"
        )
    
    # If merge_into_id is provided, merge images into that tag
    if merge_into_id:
        target_tag = db.query(Tag).filter(Tag.id == merge_into_id).first()
        if not target_tag:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Target tag not found"
            )
        
        # Update all image-tag relationships
        db.execute(
            image_tags.update()
            .where(image_tags.c.tag_id == tag_id)
            .values(tag_id=merge_into_id)
        )
        db.commit()
    
    # Delete the tag
    db.delete(tag)
    db.commit()
    
    return {"message": "Tag deleted successfully"}


@router.delete("/cleanup")
async def cleanup_unused_tags(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    # Find tags with no associated images
    unused_tags = db.query(Tag).outerjoin(image_tags).filter(
        image_tags.c.tag_id.is_(None)
    ).all()
    
    count = len(unused_tags)
    
    for tag in unused_tags:
        db.delete(tag)
    
    db.commit()
    
    return {"message": f"Deleted {count} unused tags"}