"""
Basic API Tests
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.database import Base, get_db
from app.models.user import User
from app.core.security import get_password_hash

# Create in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
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

# Create test client
client = TestClient(app)


@pytest.fixture(scope="function")
def test_db():
    """Create fresh database for each test"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_user(test_db):
    """Create a test user"""
    db = TestingSessionLocal()
    user = User(
        email="test@example.com",
        username="testuser",
        full_name="Test User",
        password_hash=get_password_hash("testpass123"),
        is_active=True,
        is_admin=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()
    return user


@pytest.fixture
def test_admin(test_db):
    """Create a test admin"""
    db = TestingSessionLocal()
    admin = User(
        email="admin@example.com",
        username="admin",
        full_name="Admin User",
        password_hash=get_password_hash("admin123"),
        is_active=True,
        is_admin=True,
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    db.close()
    return admin


@pytest.fixture
def user_token(test_user):
    """Get access token for test user"""
    response = client.post(
        "/api/v1/auth/login",
        json={"identifier": "test@example.com", "password": "testpass123"},
    )
    return response.json()["access_token"]


@pytest.fixture
def admin_token(test_admin):
    """Get access token for admin"""
    response = client.post(
        "/api/v1/auth/login",
        json={"identifier": "admin@example.com", "password": "admin123"},
    )
    return response.json()["access_token"]


# ============================================
# Health Check Tests
# ============================================

def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


# ============================================
# Authentication Tests
# ============================================

def test_register_user(test_db):
    """Test user registration"""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "password123",
            "full_name": "New User",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_register_duplicate_email(test_user):
    """Test registration with duplicate email"""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "username": "differentuser",
            "password": "password123",
        },
    )
    assert response.status_code == 409


def test_login_success(test_user):
    """Test successful login"""
    response = client.post(
        "/api/v1/auth/login",
        json={"identifier": "test@example.com", "password": "testpass123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


def test_login_invalid_credentials(test_user):
    """Test login with invalid credentials"""
    response = client.post(
        "/api/v1/auth/login",
        json={"identifier": "test@example.com", "password": "wrongpassword"},
    )
    assert response.status_code == 401


def test_get_current_user(user_token):
    """Test get current user info"""
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["username"] == "testuser"


def test_get_current_user_unauthorized():
    """Test get current user without token"""
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401


# ============================================
# Lessons Tests
# ============================================

def test_get_lessons_empty(test_db):
    """Test get lessons when database is empty"""
    response = client.get("/api/v1/lessons")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert data["items"] == []


def test_create_lesson_admin(admin_token):
    """Test create lesson as admin"""
    response = client.post(
        "/api/v1/lessons",
        json={"title": "Test Lesson", "description": "Test Description"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Lesson"
    assert data["order_index"] == 1


def test_create_lesson_non_admin(user_token):
    """Test create lesson as non-admin user"""
    response = client.post(
        "/api/v1/lessons",
        json={"title": "Test Lesson"},
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 403


def test_get_lessons_pagination(admin_token):
    """Test lessons pagination"""
    # Create multiple lessons
    for i in range(15):
        client.post(
            "/api/v1/lessons",
            json={"title": f"Lesson {i+1}"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
    
    # Get first page
    response = client.get("/api/v1/lessons?page=1&page_size=10")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 15
    assert len(data["items"]) == 10
    assert data["page"] == 1
    assert data["total_pages"] == 2


# ============================================
# Practice Tests
# ============================================

def test_get_next_sentence_empty(test_db):
    """Test get next sentence when no sentences exist"""
    response = client.get("/api/v1/practice/next")
    assert response.status_code == 404


def test_record_practice_guest(test_db, admin_token):
    """Test record practice as guest"""
    # Create lesson and sentence
    lesson_resp = client.post(
        "/api/v1/lessons",
        json={"title": "Test Lesson"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    lesson_id = lesson_resp.json()["id"]
    
    sentence_resp = client.post(
        "/api/v1/sentences",
        json={
            "lesson_id": lesson_id,
            "vi_text": "Xin chào",
            "en_text": "Hello",
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    sentence_id = sentence_resp.json()["id"]
    
    # Record practice without auth (guest)
    response = client.post(
        "/api/v1/practice/record",
        json={"sentence_id": sentence_id},
    )
    assert response.status_code == 201
    assert "not recorded for guest" in response.json()["message"]


def test_get_practice_stats_unauthorized():
    """Test get practice stats without authentication"""
    response = client.get("/api/v1/practice/stats")
    assert response.status_code == 401


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
