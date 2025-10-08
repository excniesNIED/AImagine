from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from app.core.database import get_db
from app.api.deps import get_current_active_user, get_current_admin_user
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse

router = APIRouter()


@router.get("/", response_model=List[CategoryResponse])
async def get_categories(
    skip: int = 0,
    limit: int = 100,
    include_count: bool = False,
    db: Session = Depends(get_db)
):
    if include_count:
        from app.models.image import Image
        # Count images where this category is used via category_id
        results = (
            db.query(
                Category,
                func.count(Image.id).label("image_count")
            )
            .outerjoin(Image, Image.category_id == Category.id)
            .group_by(Category.id)
            .offset(skip)
            .limit(limit)
            .all()
        )
        enriched: List[CategoryResponse] = []
        for cat, count in results:
            cat_schema = CategoryResponse.model_validate(cat)
            setattr(cat_schema, "image_count", int(count or 0))
            enriched.append(cat_schema)
        return enriched
    else:
        categories = db.query(Category).offset(skip).limit(limit).all()
        return categories


@router.get("/custom")
async def get_custom_categories(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Return distinct custom categories from images (free-text categories users entered), with counts.
    These are not in the `categories` table but exist as `Image.custom_category` values.
    """
    from app.models.image import Image

    # Query distinct custom_category with counts
    rows = (
        db.query(
            Image.custom_category.label("name"),
            func.count(Image.id).label("image_count")
        )
        .filter(Image.custom_category.isnot(None))
        .group_by(Image.custom_category)
        .order_by(func.count(Image.id).desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    # Return a simple list of dicts: { name, image_count }
    return [
        {"name": name, "image_count": int(image_count)}
        for name, image_count in rows
    ]


@router.post("/", response_model=CategoryResponse)
async def create_category(
    category: CategoryCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    # Check if category already exists
    existing = db.query(Category).filter(Category.name == category.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category already exists"
        )
    
    db_category = Category(**category.model_dump())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    
    return db_category


@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: int,
    category_update: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    # Check if new name conflicts with existing category
    if category_update.name and category_update.name != category.name:
        existing = db.query(Category).filter(Category.name == category_update.name).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category name already exists"
            )
    
    update_data = category_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(category, field, value)
    
    db.commit()
    db.refresh(category)
    
    return category


@router.delete("/{category_id}")
async def delete_category(
    category_id: int,
    merge_into_id: int = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    # If merge_into_id is provided, merge images into that category
    if merge_into_id:
        target_category = db.query(Category).filter(Category.id == merge_into_id).first()
        if not target_category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Target category not found"
            )
        
        # Update all images in this category to the target category
        from app.models.image import Image
        db.query(Image).filter(Image.category_id == category_id).update(
            {"category_id": merge_into_id}
        )
        db.commit()
    
    # Delete the category
    db.delete(category)
    db.commit()
    
    return {"message": "Category deleted successfully"}