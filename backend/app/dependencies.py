from typing import Optional
from fastapi import Depends, Header
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import decode_token
from app.core.exceptions import UnauthorizedException, ForbiddenException
from app.models.user import User
from app.schemas.auth import TokenData


def get_token_data(authorization: Optional[str] = Header(None)) -> Optional[TokenData]:
    """Extract and validate token from Authorization header."""
    if not authorization:
        return None
    
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise UnauthorizedException("Invalid authentication scheme")
        
        payload = decode_token(token)
        return TokenData(
            user_id=payload.get("user_id"),
            email=payload.get("sub"),
            is_admin=payload.get("is_admin", False),
        )
    except (ValueError, KeyError):
        raise UnauthorizedException("Invalid or expired token")


def get_current_user(
    token_data: Optional[TokenData] = Depends(get_token_data),
    db: Session = Depends(get_db),
) -> User:
    """Get current authenticated user."""
    if not token_data:
        raise UnauthorizedException("Authentication required")
    
    user = db.query(User).filter(User.id == token_data.user_id).first()
    if not user:
        raise UnauthorizedException("User not found")
    
    if not user.is_active:
        raise UnauthorizedException("Account is inactive")
    
    return user


def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    """Verify current user is admin."""
    if not current_user.is_admin:
        raise ForbiddenException("Admin access required")
    return current_user


def get_optional_user(
    token_data: Optional[TokenData] = Depends(get_token_data),
    db: Session = Depends(get_db),
) -> Optional[User]:
    """Get current user if authenticated, None otherwise (for guest mode)."""
    if not token_data:
        return None
    
    user = db.query(User).filter(User.id == token_data.user_id).first()
    if user and user.is_active:
        return user
    return None
