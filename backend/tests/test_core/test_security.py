"""Test Core Security Module"""
import pytest
from datetime import datetime, timedelta
from jose import jwt, JWTError

from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.config import settings


class TestPasswordHashing:
    """Test password hashing functions"""
    
    def test_hash_password(self):
        """Test password hashing"""
        password = "testpassword123"
        hashed = get_password_hash(password)
        
        assert hashed != password
        assert len(hashed) > 20
        assert hashed.startswith("$2b$")
    
    def test_verify_correct_password(self):
        """Test password verification with correct password"""
        password = "testpassword123"
        hashed = get_password_hash(password)
        
        assert verify_password(password, hashed) is True
    
    def test_verify_wrong_password(self):
        """Test password verification with wrong password"""
        password = "testpassword123"
        hashed = get_password_hash(password)
        
        assert verify_password("wrongpassword", hashed) is False
    
    def test_different_hashes_for_same_password(self):
        """Test same password generates different hashes (salt)"""
        password = "testpassword123"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        
        assert hash1 != hash2
        assert verify_password(password, hash1)
        assert verify_password(password, hash2)


class TestTokenCreation:
    """Test JWT token creation"""
    
    def test_create_access_token(self):
        """Test access token creation"""
        data = {"sub": "test@example.com", "user_id": "123"}
        token = create_access_token(data)
        
        assert isinstance(token, str)
        assert len(token) > 20
        
        # Decode and verify
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        assert payload["sub"] == "test@example.com"
        assert payload["user_id"] == "123"
        assert "exp" in payload
    
    def test_create_refresh_token(self):
        """Test refresh token creation"""
        data = {"sub": "test@example.com"}
        token = create_refresh_token(data)
        
        assert isinstance(token, str)
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        assert payload["sub"] == "test@example.com"
        assert "exp" in payload
    
    def test_token_expiration(self):
        """Test token contains correct expiration"""
        data = {"sub": "test@example.com"}
        token = create_access_token(data, expires_minutes=30)
        
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        exp = datetime.fromtimestamp(payload["exp"])
        now = datetime.utcnow()
        
        # Should expire in the future
        assert exp > now, "Token should not be expired"
        
        # Should have an expiration time set
        time_diff_minutes = (exp - now).total_seconds() / 60
        assert time_diff_minutes > 0, "Token expiration should be in the future"


class TestTokenDecoding:
    """Test JWT token decoding"""
    
    def test_decode_valid_token(self):
        """Test decoding valid token"""
        data = {"sub": "test@example.com", "user_id": "123"}
        token = create_access_token(data)
        
        decoded = decode_token(token)
        assert decoded["sub"] == "test@example.com"
        assert decoded["user_id"] == "123"
    
    def test_decode_expired_token(self):
        """Test decoding expired token raises error"""
        data = {"sub": "test@example.com"}
        token = create_access_token(data, expires_minutes=0)  # Expired immediately
        
        # Sleep to ensure expiration
        import time
        time.sleep(1)
        
        with pytest.raises(JWTError):
            decode_token(token)
    
    def test_decode_invalid_token(self):
        """Test decoding invalid token raises error"""
        with pytest.raises(JWTError):
            decode_token("invalid.token.here")
    
    def test_decode_tampered_token(self):
        """Test decoding tampered token raises error"""
        data = {"sub": "test@example.com"}
        token = create_access_token(data)
        
        # Tamper with token
        parts = token.split(".")
        parts[1] = parts[1][:-5] + "xxxxx"
        tampered_token = ".".join(parts)
        
        with pytest.raises(JWTError):
            decode_token(tampered_token)
