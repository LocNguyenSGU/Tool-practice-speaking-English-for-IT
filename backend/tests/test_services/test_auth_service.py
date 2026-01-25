"""
Auth Service tests
"""
import pytest
from sqlalchemy.orm import Session
from app.services.auth_service import AuthService
from app.schemas.auth import RegisterRequest, LoginRequest
from app.models.user import User
from app.core.exceptions import ConflictException, UnauthorizedException
from app.core.security import verify_password


class TestAuthService:
    """Test authentication service"""
    
    def test_register_user_success(self, db: Session):
        """Test successful user registration"""
        data = RegisterRequest(
            email="test@example.com",
            username="testuser",
            password="password123"
        )
        
        user = AuthService.register_user(db, data)
        
        assert user is not None
        assert user.email == "test@example.com"
        assert user.username == "testuser"
        assert verify_password("password123", user.hashed_password)
        assert user.is_active is True
        assert user.is_admin is False
    
    def test_register_user_duplicate_email(self, db: Session, test_user: User):
        """Test registration with duplicate email fails"""
        data = RegisterRequest(
            email="test@example.com",  # Same as test_user
            username="newuser",
            password="password123"
        )
        
        with pytest.raises(ConflictException) as exc:
            AuthService.register_user(db, data)
        
        assert "already registered" in str(exc.value.detail).lower()
    
    def test_register_user_duplicate_username(self, db: Session, test_user: User):
        """Test registration with duplicate username fails"""
        data = RegisterRequest(
            email="new@example.com",
            username="testuser",  # Same as test_user
            password="password123"
        )
        
        with pytest.raises(ConflictException) as exc:
            AuthService.register_user(db, data)
        
        assert "already registered" in str(exc.value.detail).lower()
    
    def test_authenticate_user_success(self, db: Session, test_user: User):
        """Test successful authentication"""
        data = LoginRequest(
            email="test@example.com",
            password="testpass123"
        )
        
        user = AuthService.authenticate_user(db, data)
        
        assert user is not None
        assert user.id == test_user.id
        assert user.email == test_user.email
    
    def test_authenticate_user_wrong_password(self, db: Session, test_user: User):
        """Test authentication with wrong password fails"""
        data = LoginRequest(
            email="test@example.com",
            password="wrongpassword"
        )
        
        with pytest.raises(UnauthorizedException) as exc:
            AuthService.authenticate_user(db, data)
        
        assert "invalid" in str(exc.value.detail).lower()
    
    def test_authenticate_user_not_found(self, db: Session):
        """Test authentication with non-existent user fails"""
        data = LoginRequest(
            email="notfound@example.com",
            password="password123"
        )
        
        with pytest.raises(UnauthorizedException) as exc:
            AuthService.authenticate_user(db, data)
        
        assert "invalid" in str(exc.value.detail).lower()
    
    def test_authenticate_inactive_user(self, db: Session):
        """Test authentication with inactive user fails"""
        from app.core.security import get_password_hash
        
        # Create inactive user with properly hashed password
        user = User(
            email="inactive@example.com",
            username="inactive",
            hashed_password=get_password_hash("password"),
            is_active=False
        )
        db.add(user)
        db.commit()
        
        data = LoginRequest(
            email="inactive@example.com",
            password="password"
        )
        
        # Should fail because user is inactive
        with pytest.raises(UnauthorizedException):
            AuthService.authenticate_user(db, data)
    
    def test_create_tokens(self, test_user: User):
        """Test token creation"""
        tokens = AuthService.create_tokens(test_user)
        
        assert "access_token" in tokens
        assert "refresh_token" in tokens
        assert tokens["token_type"] == "bearer"
        assert isinstance(tokens["access_token"], str)
        assert isinstance(tokens["refresh_token"], str)
        assert len(tokens["access_token"]) > 0
        assert len(tokens["refresh_token"]) > 0
