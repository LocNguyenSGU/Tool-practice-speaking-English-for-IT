"""
Database Seeding Script

Usage:
    python seed_data.py
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.models.lesson import Lesson
from app.models.sentence import Sentence
from app.models.user import User
from app.core.security import get_password_hash


def seed_database():
    """Seed database with initial data"""
    db = SessionLocal()
    
    try:
        print("🌱 Starting database seeding...")
        
        # Create admin user
        admin_exists = db.query(User).filter(User.email == "admin@example.com").first()
        if not admin_exists:
            admin = User(
                email="admin@example.com",
                username="admin",
                full_name="Administrator",
                password_hash=get_password_hash("admin123"),
                is_admin=True,
                is_active=True,
            )
            db.add(admin)
            print("✅ Admin user created (email: admin@example.com, password: admin123)")
        else:
            print("ℹ️  Admin user already exists")
        
        # Create sample lessons
        lesson1 = db.query(Lesson).filter(Lesson.title == "Greetings").first()
        if not lesson1:
            lesson1 = Lesson(
                title="Greetings",
                description="Basic greeting phrases in Vietnamese and English",
                order_index=1,
            )
            db.add(lesson1)
            db.flush()  # Get lesson1.id
            
            # Sample sentences for lesson 1
            sentences1 = [
                ("Xin chào", "Hello"),
                ("Chào buổi sáng", "Good morning"),
                ("Chào buổi chiều", "Good afternoon"),
                ("Chào buổi tối", "Good evening"),
                ("Tạm biệt", "Goodbye"),
                ("Hẹn gặp lại", "See you later"),
                ("Rất vui được gặp bạn", "Nice to meet you"),
                ("Bạn khỏe không?", "How are you?"),
                ("Tôi khỏe, cảm ơn", "I'm fine, thank you"),
                ("Cảm ơn", "Thank you"),
            ]
            
            for idx, (vi, en) in enumerate(sentences1, 1):
                sentence = Sentence(
                    lesson_id=lesson1.id,
                    vi_text=vi,
                    en_text=en,
                    order_index=idx,
                )
                db.add(sentence)
            
            print(f"✅ Lesson 1 created: {lesson1.title} ({len(sentences1)} sentences)")
        else:
            print("ℹ️  Lesson 'Greetings' already exists")
        
        # Create lesson 2
        lesson2 = db.query(Lesson).filter(Lesson.title == "Numbers").first()
        if not lesson2:
            lesson2 = Lesson(
                title="Numbers",
                description="Learn to count from 1 to 10 in Vietnamese",
                order_index=2,
            )
            db.add(lesson2)
            db.flush()
            
            sentences2 = [
                ("Một", "One"),
                ("Hai", "Two"),
                ("Ba", "Three"),
                ("Bốn", "Four"),
                ("Năm", "Five"),
                ("Sáu", "Six"),
                ("Bảy", "Seven"),
                ("Tám", "Eight"),
                ("Chín", "Nine"),
                ("Mười", "Ten"),
            ]
            
            for idx, (vi, en) in enumerate(sentences2, 1):
                sentence = Sentence(
                    lesson_id=lesson2.id,
                    vi_text=vi,
                    en_text=en,
                    order_index=idx,
                )
                db.add(sentence)
            
            print(f"✅ Lesson 2 created: {lesson2.title} ({len(sentences2)} sentences)")
        else:
            print("ℹ️  Lesson 'Numbers' already exists")
        
        # Create lesson 3
        lesson3 = db.query(Lesson).filter(Lesson.title == "Common Phrases").first()
        if not lesson3:
            lesson3 = Lesson(
                title="Common Phrases",
                description="Everyday phrases for basic conversation",
                order_index=3,
            )
            db.add(lesson3)
            db.flush()
            
            sentences3 = [
                ("Xin lỗi", "Excuse me / Sorry"),
                ("Không sao", "No problem / It's okay"),
                ("Vâng", "Yes"),
                ("Không", "No"),
                ("Tôi không hiểu", "I don't understand"),
                ("Bạn nói tiếng Anh được không?", "Do you speak English?"),
                ("Tôi đang học tiếng Việt", "I'm learning Vietnamese"),
                ("Giúp tôi với", "Help me please"),
                ("Bao nhiêu tiền?", "How much is it?"),
                ("Ở đâu?", "Where is it?"),
            ]
            
            for idx, (vi, en) in enumerate(sentences3, 1):
                sentence = Sentence(
                    lesson_id=lesson3.id,
                    vi_text=vi,
                    en_text=en,
                    order_index=idx,
                )
                db.add(sentence)
            
            print(f"✅ Lesson 3 created: {lesson3.title} ({len(sentences3)} sentences)")
        else:
            print("ℹ️  Lesson 'Common Phrases' already exists")
        
        db.commit()
        print("\n🎉 Database seeding completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error during seeding: {e}")
        db.rollback()
        raise
    
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
