from sqlalchemy import Column, Integer, String, DateTime, Table, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

# Association table for many-to-many relationship between images and tags
image_tags = Table(
    'image_tags',
    Base.metadata,
    Column('image_id', Integer, ForeignKey('images.id', ondelete='CASCADE'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id', ondelete='CASCADE'), primary_key=True)
)


class Tag(Base):
    __tablename__ = "tags"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), index=True, nullable=False)
    description = Column(String(200), nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # null means admin-created tag
    is_public = Column(Boolean, default=True, nullable=False)  # whether tag is visible to other users
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    owner = relationship("User", back_populates="tags")
    images = relationship("Image", secondary=image_tags, back_populates="tags")