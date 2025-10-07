#!/usr/bin/env python3
"""
AI Gallery Initialization Script
This script helps set up the project for first-time use
"""

import os
import sys
import sqlite3
import subprocess
from pathlib import Path

def create_env_file():
    """Create .env file from template if it doesn't exist"""
    env_path = Path(".env")
    example_path = Path(".env.example")

    if not env_path.exists() and example_path.exists():
        print("Creating .env file from template...")
        with open(example_path, 'r') as f:
            content = f.read()
        with open(env_path, 'w') as f:
            f.write(content)
        print("✓ .env file created")
        print("⚠️  Please edit .env file with your configuration before running the application")
    elif env_path.exists():
        print("✓ .env file already exists")
    else:
        print("⚠️  No .env.example file found")

def init_database():
    """Initialize the SQLite database with tables"""
    print("Initializing database...")
    try:
        # Check if we're in backend directory
        if not Path("app").exists():
            print("Changing to backend directory...")
            os.chdir("backend")

        # Import and create tables
        from app.core.database import Base, engine
        from app.models import user, image, category, tag, model

        Base.metadata.create_all(bind=engine)
        print("✓ Database initialized successfully")

        # Create default data
        create_default_data()

    except Exception as e:
        print(f"✗ Failed to initialize database: {e}")
        sys.exit(1)

def create_default_data():
    """Create default categories, tags, and models"""
    from app.core.database import SessionLocal
    from app.models.category import Category
    from app.models.tag import Tag
    from app.models.model import Model

    db = SessionLocal()
    try:
        # Create default categories
        if db.query(Category).count() == 0:
            categories = [
                Category(name="人物"),
                Category(name="风景"),
                Category(name="动物"),
                Category(name="建筑"),
                Category(name="艺术"),
                Category(name="科幻"),
                Category(name="动漫"),
                Category(name="其他")
            ]
            db.add_all(categories)
            print("✓ Default categories created")

        # Create default tags
        if db.query(Tag).count() == 0:
            tags = [
                Tag(name="高质量"),
                Tag(name="大师作品"),
                Tag(name="杰作"),
                Tag(name="最佳品质"),
                Tag(name="4K"),
                Tag(name="8K"),
                Tag(name="写实风格"),
                Tag(name="超精细"),
                Tag(name="电影光效"),
                Tag(name="复杂细节"),
                Tag(name="虚幻引擎"),
                Tag(name="OC渲染器"),
                Tag(name="概念艺术"),
                Tag(name="数字绘画"),
                Tag(name="插画"),
                Tag(name="原画")
            ]
            db.add_all(tags)
            print("✓ Default tags created")

        # Create default models
        if db.query(Model).count() == 0:
            models = [
                Model(name="Stable Diffusion"),
                Model(name="Midjourney"),
                Model(name="DALL-E"),
                Model(name="NovelAI"),
                Model(name="Waifu Diffusion"),
                Model(name="ChilloutMix"),
                Model(name="Anything V4/V5"),
                Model(name="AbyssOrangeMix"),
                Model(name="MeinaMix"),
                Model(name="Custom Model")
            ]
            db.add_all(models)
            print("✓ Default models created")

        db.commit()
    except Exception as e:
        db.rollback()
        print(f"✗ Failed to create default data: {e}")
    finally:
        db.close()

def check_dependencies():
    """Check if required dependencies are installed"""
    print("Checking dependencies...")

    # Check Python version
    if sys.version_info < (3, 9):
        print("✗ Python 3.9 or higher is required")
        sys.exit(1)
    print(f"✓ Python {sys.version.split()[0]}")

    # Check if Docker is available
    try:
        subprocess.run(["docker", "--version"], check=True, capture_output=True)
        print("✓ Docker is available")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️  Docker not found. Install Docker for easier deployment")

    # Check if Node.js is available
    try:
        subprocess.run(["node", "--version"], check=True, capture_output=True)
        print("✓ Node.js is available")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️  Node.js not found. Install Node.js for frontend development")

def run_with_docker():
    """Run the application using Docker Compose"""
    print("Starting application with Docker...")
    try:
        subprocess.run(["docker-compose", "up", "-d"], check=True)
        print("\n✓ Application started successfully!")
        print("\nAccess the application at:")
        print("  Frontend: http://localhost:4321")
        print("  Backend API: http://localhost:8000")
        print("  API Documentation: http://localhost:8000/docs")
        print("  Alist: http://localhost:5244")
        print("\nDefault Alist credentials:")
        print("  Username: admin")
        print("  Password: admin123")
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to start application: {e}")
        sys.exit(1)

def run_locally():
    """Run the application locally for development"""
    print("Starting application locally...")

    # Start backend
    print("\n1. Starting backend server...")
    backend_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"],
        cwd="backend"
    )

    # Start frontend
    print("2. Starting frontend server...")
    frontend_process = subprocess.Popen(
        ["npm", "run", "dev"],
        cwd="frontend"
    )

    print("\n✓ Application started successfully!")
    print("\nAccess the application at:")
    print("  Frontend: http://localhost:4321")
    print("  Backend API: http://localhost:8000")
    print("  API Documentation: http://localhost:8000/docs")

    print("\nPress Ctrl+C to stop the servers")

    try:
        # Wait for user to stop
        backend_process.wait()
    except KeyboardInterrupt:
        print("\nStopping servers...")
        backend_process.terminate()
        frontend_process.terminate()
        backend_process.wait()
        frontend_process.wait()
        print("✓ Servers stopped")

def main():
    """Main function"""
    print("=" * 60)
    print("  AI Gallery (AImagine) Initialization")
    print("=" * 60)
    print()

    # Check current directory
    if not Path("backend").exists() or not Path("frontend").exists():
        print("✗ Please run this script from the project root directory")
        sys.exit(1)

    # Check dependencies
    check_dependencies()
    print()

    # Create .env file
    create_env_file()
    print()

    # Initialize database
    init_database()
    print()

    # Ask user how to run
    print("How would you like to run the application?")
    print("1. With Docker (recommended)")
    print("2. Locally (for development)")

    choice = input("\nEnter your choice (1 or 2): ").strip()

    if choice == "1":
        print()
        run_with_docker()
    elif choice == "2":
        print()
        run_locally()
    else:
        print("Invalid choice. Exiting...")
        sys.exit(1)

if __name__ == "__main__":
    main()