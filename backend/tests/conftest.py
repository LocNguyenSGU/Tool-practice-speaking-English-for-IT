"""
Shared Test Fixtures and Configuration
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from sqlalchemy.types import TypeDecorator, CHAR
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.main import app
from app.core.database import Base, get_db
from app.models.user import User
from app.models.lesson import Lesson
from app.models.sentence import Sentence
from app.core.security import get_password_hash


# Create in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


# Register event to patch UUIDs before table creation
@event.listens_for(Base.metadata, "before_create")
def receive_before_create(target, connection, **kw):
    """Patch UUID columns and defaults before creating tables in SQLite"""
    from sqlalchemy import String
    
    for table in target.tables.values():
        for column in table.columns:
            if isinstance(column.type, UUID):
                # Replace UUID type with String(36)
                column.type = String(36)
                # Patch default function to return string UUID
                if column.default is not None and hasattr(column.default, 'arg'):
                    original_fn = column.default.arg
                    if callable(original_fn):
                        # SQLAlchemy passes context to default functions
                        column.default.arg = lambda ctx=None: str(uuid.uuid4())
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing"""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Override dependency
app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function")
def db() -> Session:
    """Create fresh database session for each test"""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db) -> TestClient:
    """Create test client"""
    return TestClient(app)


@pytest.fixture
def test_user(db: Session) -> User:
    """Create a test user"""
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password=get_password_hash("testpass123"),
        is_active=True,
        is_admin=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def test_admin(db: Session) -> User:
    """Create a test admin"""
    admin = User(
        email="admin@example.com",
        username="admin",
        hashed_password=get_password_hash("admin123"),
        is_active=True,
        is_admin=True,
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin


@pytest.fixture
def user_token(test_user: User) -> str:
    """Get access token for test user"""
    from app.core.security import create_access_token
    token_data = {
        "sub": test_user.email,
        "user_id": str(test_user.id),
        "is_admin": test_user.is_admin,
    }
    return create_access_token(token_data)


@pytest.fixture
def admin_token(test_admin: User) -> str:
    """Get access token for admin"""
    from app.core.security import create_access_token
    token_data = {
        "sub": test_admin.email,
        "user_id": str(test_admin.id),
        "is_admin": test_admin.is_admin,
    }
    return create_access_token(token_data)


@pytest.fixture
def test_lesson(db: Session) -> Lesson:
    """Create a test lesson"""
    lesson = Lesson(
        title="Test Lesson",
        description="Test Description",
        order_index=1,
    )
    db.add(lesson)
    db.commit()
    db.refresh(lesson)
    return lesson


@pytest.fixture
def test_sentence(db: Session, test_lesson: Lesson) -> Sentence:
    """Create a test sentence"""
    sentence = Sentence(
        lesson_id=test_lesson.id,
        vi_text="Xin chào",
        en_text="Hello",
        order_index=1,
    )
    db.add(sentence)
    db.commit()
    db.refresh(sentence)
    return sentence


@pytest.fixture
def test_sentences(db: Session, test_lesson: Lesson) -> list[Sentence]:
    """Create multiple test sentences"""
    sentences = []
    texts = [
        ("Xin chào", "Hello"),
        ("Tạm biệt", "Goodbye"),
        ("Cảm ơn", "Thank you"),
    ]
    for i, (vi, en) in enumerate(texts, 1):
        sentence = Sentence(
            lesson_id=test_lesson.id,
            vi_text=vi,
            en_text=en,
            order_index=i,
        )
        db.add(sentence)
        sentences.append(sentence)
    
    db.commit()
    for s in sentences:
        db.refresh(s)
    return sentences
