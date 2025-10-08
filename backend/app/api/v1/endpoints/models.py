from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from app.core.database import get_db
from app.api.deps import get_current_active_user, get_current_admin_user
from app.models.model import Model
from app.schemas.model import ModelCreate, ModelUpdate, ModelResponse

router = APIRouter()


@router.get("/", response_model=List[ModelResponse])
async def get_models(
    skip: int = 0,
    limit: int = 100,
    include_count: bool = False,
    db: Session = Depends(get_db)
):
    if include_count:
        from app.models.image import Image
        results = (
            db.query(
                Model,
                func.count(Image.id).label("image_count")
            )
            .outerjoin(Image, Image.model_id == Model.id)
            .group_by(Model.id)
            .offset(skip)
            .limit(limit)
            .all()
        )
        enriched: List[ModelResponse] = []
        for mdl, count in results:
            mdl_schema = ModelResponse.model_validate(mdl)
            setattr(mdl_schema, "image_count", int(count or 0))
            enriched.append(mdl_schema)
        return enriched
    else:
        models = db.query(Model).offset(skip).limit(limit).all()
        return models


@router.get("/custom")
async def get_custom_models(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Return distinct custom models from images (free-text models users entered), with counts.
    These are not in the `models` table but exist as `Image.custom_model` values.
    """
    from app.models.image import Image

    rows = (
        db.query(
            Image.custom_model.label("name"),
            func.count(Image.id).label("image_count")
        )
        .filter(Image.custom_model.isnot(None))
        .group_by(Image.custom_model)
        .order_by(func.count(Image.id).desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    return [
        {"name": name, "image_count": int(image_count)}
        for name, image_count in rows
    ]


@router.post("/", response_model=ModelResponse)
async def create_model(
    model: ModelCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    # Check if model already exists
    existing = db.query(Model).filter(Model.name == model.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Model already exists"
        )
    
    db_model = Model(**model.model_dump())
    db.add(db_model)
    db.commit()
    db.refresh(db_model)
    
    return db_model


@router.put("/{model_id}", response_model=ModelResponse)
async def update_model(
    model_id: int,
    model_update: ModelUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    model = db.query(Model).filter(Model.id == model_id).first()
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model not found"
        )
    
    # Check if new name conflicts with existing model
    if model_update.name and model_update.name != model.name:
        existing = db.query(Model).filter(Model.name == model_update.name).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Model name already exists"
            )
    
    update_data = model_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(model, field, value)
    
    db.commit()
    db.refresh(model)
    
    return model


@router.delete("/{model_id}")
async def delete_model(
    model_id: int,
    merge_into_id: int = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    model = db.query(Model).filter(Model.id == model_id).first()
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model not found"
        )
    
    # If merge_into_id is provided, merge images into that model
    if merge_into_id:
        target_model = db.query(Model).filter(Model.id == merge_into_id).first()
        if not target_model:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Target model not found"
            )
        
        # Update all images using this model to the target model
        from app.models.image import Image
        db.query(Image).filter(Image.model_id == model_id).update(
            {"model_id": merge_into_id}
        )
        db.commit()
    
    # Delete the model
    db.delete(model)
    db.commit()
    
    return {"message": "Model deleted successfully"}