"""
Authentication Endpoints
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_token
from app.core.exceptions import UnauthorizedException
from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    TokenResponse,
    TokenRefreshRequest,
)
from app.schemas.user import UserPublic
from app.services.auth_service import AuthService
from app.dependencies import get_current_user

router = APIRouter()


@router.post("/auth/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """
    Register a new user
    
    - **email**: Valid email address (unique)
    - **username**: Username 3-50 characters (unique)
    - **password**: Password min 6 characters
    - **full_name**: Optional full name
    """
    user = AuthService.register_user(db, request)
    tokens = AuthService.create_tokens(user)
    return tokens


@router.post("/auth/login", response_model=TokenResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    Login with email and password
    
    - **email**: User email address
    - **password**: User password
    """
    user = AuthService.authenticate_user(db, request)
    tokens = AuthService.create_tokens(user)
    return tokens


@router.post("/auth/refresh", response_model=TokenResponse)
async def refresh_token(request: TokenRefreshRequest, db: Session = Depends(get_db)):
    """
    Refresh access token using refresh token
    
    - **refresh_token**: Valid refresh token
    """
    from app.models.user import User
    from jose import JWTError
    
    # Decode refresh token
    try:
        token_data = decode_token(request.refresh_token)
        if not token_data or token_data.get("type") != "refresh":
            raise UnauthorizedException("Invalid refresh token")
    except JWTError:
        raise UnauthorizedException("Invalid or expired refresh token")
    
    # Get user - token sub is email
    user_email = token_data.get("sub")
    if not user_email:
        raise UnauthorizedException("Invalid token data")
    
    user = db.query(User).filter(User.email == user_email).first()
    if not user or not user.is_active:
        raise UnauthorizedException("User not found or inactive")
    
    # Create new tokens
    tokens = AuthService.create_tokens(user)
    return tokens


@router.get("/auth/me", response_model=UserPublic)
async def get_current_user_info(current_user = Depends(get_current_user)):
    """
    Get current authenticated user information
    
    Requires: Bearer token in Authorization header
    """
    return current_user
