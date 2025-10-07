from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
from .tag import image_tags  # Import the association table


class Image(Base):
    __tablename__ = "images"
    
    id = Column(Integer, primary_key=True, index=True)
    prompt = Column(Text, nullable=False)
    negative_prompt = Column(Text, nullable=True)
    alist_url = Column(String(500), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_size = Column(Integer, nullable=True)
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    is_public = Column(Boolean, default=False, nullable=False)  # whether image is visible in public gallery
    custom_model = Column(String(100), nullable=True)  # custom model name if user selects "other"
    custom_category = Column(String(100), nullable=True)  # custom category name if user selects "other"
    
    # Foreign keys
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    model_id = Column(Integer, ForeignKey("models.id"), nullable=True)  # nullable to allow custom model
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)  # nullable to allow custom category
    parent_image_id = Column(Integer, ForeignKey("images.id"), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    owner = relationship("User", back_populates="images")
    model = relationship("Model", back_populates="images")
    category = relationship("Category", back_populates="images")
    parent_image = relationship("Image", remote_side=[id], back_populates="child_images")
    child_images = relationship("Image", back_populates="parent_image")
    tags = relationship("Tag", secondary=image_tags, back_populates="images")
    parameters = relationship("KeyValueParameter", back_populates="image", cascade="all, delete-orphan")
    version_history = relationship("VersionHistory", foreign_keys="[VersionHistory.parent_image_id]", back_populates="parent_image")


class VersionHistory(Base):
    __tablename__ = "version_history"
    
    id = Column(Integer, primary_key=True, index=True)
    parent_image_id = Column(Integer, ForeignKey("images.id"), nullable=False)
    child_image_id = Column(Integer, ForeignKey("images.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    parent_image = relationship("Image", foreign_keys=[parent_image_id], back_populates="version_history")


class KeyValueParameter(Base):
    __tablename__ = "key_value_parameters"
    
    id = Column(Integer, primary_key=True, index=True)
    image_id = Column(Integer, ForeignKey("images.id", ondelete="CASCADE"), nullable=False)
    key = Column(String(100), nullable=False)
    value = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    image = relationship("Image", back_populates="parameters")