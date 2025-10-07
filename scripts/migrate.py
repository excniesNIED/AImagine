#!/usr/bin/env python3
"""
Database migration script for AI Gallery
"""

import sys
import os
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent / "backend"))

from sqlalchemy import inspect
from app.core.database import engine, SessionLocal
from app.models import Base, User, Category, Tag, Model, Image

def check_migration_needed():
    """Check if database migration is needed"""
    inspector = inspect(engine)
    tables = inspector.get_table_names()

    if not tables:
        return True

    # Check if version_history table exists
    if "version_history" not in tables:
        return True

    # Check if key_value_parameters table exists
    if "key_value_parameters" not in tables:
        return True

    return False

def run_migration():
    """Run database migration"""
    print("Running database migration...")

    # Create all tables
    Base.metadata.create_all(bind=engine)

    # Migrate existing data if needed
    db = SessionLocal()
    try:
        # Add any migration logic here

        print("✓ Migration completed successfully")
    except Exception as e:
        print(f"✗ Migration failed: {e}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()

def create_admin_user():
    """Create an admin user if none exists"""
    db = SessionLocal()
    try:
        admin_count = db.query(User).filter(User.role == "admin").count()
        if admin_count == 0:
            print("No admin user found. Creating default admin user...")
            admin = User(
                username="admin",
                email="admin@example.com",
                role="admin",
                is_active=True
            )
            admin.set_password("admin123")
            db.add(admin)
            db.commit()
            print("✓ Default admin user created")
            print("  Username: admin")
            print("  Password: admin123")
            print("  Please change the password after first login!")
        else:
            print(f"✓ Found {admin_count} admin user(s)")
    except Exception as e:
        print(f"✗ Failed to create admin user: {e}")
        db.rollback()
    finally:
        db.close()

def main():
    """Main migration function"""
    print("=" * 50)
    print("  AI Gallery Database Migration")
    print("=" * 50)
    print()

    # Change to backend directory
    os.chdir(Path(__file__).parent.parent / "backend")

    # Check if migration is needed
    if not check_migration_needed():
        print("Database is up to date")
        create_admin_user()
        return

    print("Database migration is required")

    # Ask for confirmation
    confirm = input("Do you want to proceed with migration? (y/N): ").strip().lower()
    if confirm != 'y':
        print("Migration cancelled")
        return

    # Run migration
    run_migration()

    # Create admin user if needed
    create_admin_user()

    print()
    print("Migration completed successfully!")

if __name__ == "__main__":
    main()