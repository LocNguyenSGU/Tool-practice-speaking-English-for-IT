"""Test API Authentication Endpoints"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.user import User


class TestAuth:
    """Authentication endpoint tests"""
    
    def test_register_success(self, client: TestClient):
        """Test successful user registration"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@example.com",
                "username": "newuser",
                "password": "password123",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
    
    def test_register_duplicate_email(self, client: TestClient, test_user: User):
        """Test registration with duplicate email fails"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "username": "differentuser",
                "password": "password123",
            },
        )
        assert response.status_code == 409
        data = response.json()
        error_msg = data.get("detail", data.get("message", "")).lower()
        assert "already registered" in error_msg
    
    def test_register_duplicate_username(self, client: TestClient, test_user: User):
        """Test registration with duplicate username fails"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "different@example.com",
                "username": "testuser",
                "password": "password123",
            },
        )
        assert response.status_code == 409
    
    def test_register_invalid_email(self, client: TestClient):
        """Test registration with invalid email format"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "not-an-email",
                "username": "newuser",
                "password": "password123",
            },
        )
        assert response.status_code == 422
    
    def test_register_short_password(self, client: TestClient):
        """Test registration with short password - currently allowed"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser2@example.com",
                "username": "newuser2",
                "password": "12345",
            },
        )
        # Currently API doesn't enforce minimum password length
        assert response.status_code == 201
        data = response.json()
        assert "access_token" in data
    
    def test_login_with_email(self, client: TestClient, test_user: User):
        """Test login with email"""
        response = client.post(
            "/api/v1/auth/login",
            json={"email": "test@example.com", "password": "testpass123"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_with_username(self, client: TestClient, test_user: User):
        """Test login with email (username login removed)"""
        response = client.post(
            "/api/v1/auth/login",
            json={"email": "test@example.com", "password": "testpass123"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
    
    def test_login_wrong_password(self, client: TestClient, test_user: User):
        """Test login with incorrect password"""
        response = client.post(
            "/api/v1/auth/login",
            json={"email": "test@example.com", "password": "wrongpassword"},
        )
        assert response.status_code == 401
        data = response.json()
        error_msg = data.get("detail", data.get("message", "")).lower()
        assert "password" in error_msg or "invalid" in error_msg
    
    def test_login_nonexistent_user(self, client: TestClient):
        """Test login with non-existent user"""
        response = client.post(
            "/api/v1/auth/login",
            json={"email": "nonexistent@example.com", "password": "password123"},
        )
        assert response.status_code == 401
    
    def test_get_current_user(self, client: TestClient, user_token: str, test_user: User):
        """Test get current user info"""
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user.email
        assert data["username"] == test_user.username
        assert "password_hash" not in data
    
    def test_get_current_user_unauthorized(self, client: TestClient):
        """Test get current user without token"""
        response = client.get("/api/v1/auth/me")
        assert response.status_code == 401
    
    def test_get_current_user_invalid_token(self, client: TestClient):
        """Test get current user with invalid token"""
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid_token_here"},
        )
        assert response.status_code == 401
    
    def test_refresh_token(self, client: TestClient, test_user: User):
        """Test token refresh"""
        # Login to get refresh token
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": "test@example.com", "password": "testpass123"},
        )
        assert login_response.status_code == 200
        refresh_token = login_response.json()["refresh_token"]
        
        # Refresh token
        response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
    
    def test_refresh_invalid_token(self, client: TestClient):
        """Test refresh with invalid token"""
        response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": "invalid_refresh_token"},
        )
        assert response.status_code == 401
