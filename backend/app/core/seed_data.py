"""
Database Seed Data
Creates default users on first startup if none exist.
"""
from sqlalchemy.orm import Session
from app.models.user import User
from app.core.security import get_password_hash
from app.config import settings


def seed_database(SessionLocal) -> None:
    """
    Create default users if the database is empty.
    
    Creates:
    - Admin user (from settings.first_admin_email/password)
    - Demo user (from settings.first_demo_email/password)
    """
    db: Session = SessionLocal()
    
    try:
        # Check if any users exist
        user_count = db.query(User).count()
        
        if user_count > 0:
            print(f"📦 Database already has {user_count} user(s), skipping seed")
            return
        
        print("📦 Seeding database with default users...")
        
        # Create admin user
        admin_user = User(
            email=settings.first_admin_email,
            username="admin",
            hashed_password=get_password_hash(settings.first_admin_password),
            is_active=True,
            is_admin=True,
        )
        db.add(admin_user)
        print(f"  ✓ Created admin user: {settings.first_admin_email}")
        
        # Create demo user
        demo_user = User(
            email=settings.first_demo_email,
            username="demo",
            hashed_password=get_password_hash(settings.first_demo_password),
            is_active=True,
            is_admin=False,
        )
        db.add(demo_user)
        print(f"  ✓ Created demo user: {settings.first_demo_email}")
        
        db.commit()
        print("✅ Database seeded successfully!")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding database: {e}")
        raise
    finally:
        db.close()
