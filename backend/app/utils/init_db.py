from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models import User, Model, Category, Tag
from app.models.user import UserRole
from app.core.security import get_password_hash
import logging


def init_db() -> None:
    db = SessionLocal()
    
    try:
        created_anything = False
        # Create default admin user
        admin_user = db.query(User).filter(User.username == "admin").first()
        if not admin_user:
            admin_user = User(
                username="admin",
                email="admin@example.com",
                hashed_password=get_password_hash("admin123"),
                role=UserRole.admin
            )
            db.add(admin_user)
            db.commit()
            created_anything = True
        
        # Create default models
        default_models = [
            {"name": "Stable Diffusion 5.0", "description": "Advanced text-to-image model"},
            {"name": "DALL-E 4.0", "description": "OpenAI's image generation model"},
            {"name": "MidJourney V6.1", "description": "High-quality artistic image generator"},
            {"name": "Seedream 4.0", "description": "Creative AI image model"},
            {"name": "混元图像 3.0", "description": "Tencent's Chinese image model"},
            {"name": "HiDream-I1", "description": "Dream-inspired image generator"},
            {"name": "Imagen 3", "description": "Google's image generation model"},
            {"name": "Nano Banana", "description": "Compact and efficient model"},
            {"name": "即梦 4.0", "description": "Chinese dream-themed model"},
        ]
        
        for model_data in default_models:
            model = db.query(Model).filter(Model.name == model_data["name"]).first()
            if not model:
                model = Model(**model_data)
                db.add(model)
                created_anything = True
        
        # Create default categories
        default_categories = [
            {"name": "风景", "description": "Natural landscapes and scenery"},
            {"name": "人物", "description": "Portraits and character art"},
            {"name": "二次元", "description": "Anime and manga style art"},
            {"name": "抽象", "description": "Abstract and conceptual art"},
            {"name": "建筑", "description": "Architecture and buildings"},
            {"name": "动物", "description": "Animals and wildlife"},
            {"name": "科幻", "description": "Science fiction themes"},
        ]
        
        for cat_data in default_categories:
            category = db.query(Category).filter(Category.name == cat_data["name"]).first()
            if not category:
                category = Category(**cat_data)
                db.add(category)
                created_anything = True
        
        db.commit()
        if created_anything:
            logging.getLogger(__name__).info("Database initialized with default data.")
        
    except Exception as e:
        logging.getLogger(__name__).exception("Error initializing database: %s", e)
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    init_db()