"""Test Core Exceptions"""
import pytest
from fastapi import status

from app.core.exceptions import (
    NotFoundException,
    UnauthorizedException,
    ForbiddenException,
    BadRequestException,
    ConflictException,
)


class TestCustomExceptions:
    """Test custom exception classes"""
    
    def test_not_found_exception(self):
        """Test NotFoundException"""
        exc = NotFoundException("Resource not found")
        assert exc.status_code == status.HTTP_404_NOT_FOUND
        assert exc.detail == "Resource not found"
    
    def test_not_found_default_message(self):
        """Test NotFoundException with default message"""
        exc = NotFoundException()
        assert exc.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in exc.detail.lower()
    
    def test_unauthorized_exception(self):
        """Test UnauthorizedException"""
        exc = UnauthorizedException("Invalid token")
        assert exc.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc.detail == "Invalid token"
    
    def test_forbidden_exception(self):
        """Test ForbiddenException"""
        exc = ForbiddenException("Admin required")
        assert exc.status_code == status.HTTP_403_FORBIDDEN
        assert exc.detail == "Admin required"
    
    def test_bad_request_exception(self):
        """Test BadRequestException"""
        exc = BadRequestException("Invalid data")
        assert exc.status_code == status.HTTP_400_BAD_REQUEST
        assert exc.detail == "Invalid data"
    
    def test_conflict_exception(self):
        """Test ConflictException"""
        exc = ConflictException("Already exists")
        assert exc.status_code == status.HTTP_409_CONFLICT
        assert exc.detail == "Already exists"
    
    def test_exception_can_be_raised(self):
        """Test exceptions can be raised and caught"""
        with pytest.raises(NotFoundException) as exc_info:
            raise NotFoundException("Test not found")
        
        assert exc_info.value.status_code == 404
        assert "Test not found" in str(exc_info.value.detail)
