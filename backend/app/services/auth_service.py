from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.auth import RegisterRequest, LoginRequest, TokenData
from app.core.security import get_password_hash, verify_password, create_access_token, create_refresh_token
from app.core.exceptions import UnauthorizedException, ConflictException


class AuthService:
    @staticmethod
    def register_user(db: Session, data: RegisterRequest) -> User:
        """Register a new user."""
        # Check if user exists
        existing = db.query(User).filter(
            (User.email == data.email) | (User.username == data.username)
        ).first()
        
        if existing:
            raise ConflictException("Email or username already registered")
        
        # Create user
        user = User(
            email=data.email,
            username=data.username,
            hashed_password=get_password_hash(data.password),
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    
    @staticmethod
    def authenticate_user(db: Session, data: LoginRequest) -> User:
        """Authenticate user and return user object."""
        user = db.query(User).filter(User.email == data.email).first()
        
        if not user or not verify_password(data.password, user.hashed_password):
            raise UnauthorizedException("Invalid email or password")
        
        if not user.is_active:
            raise UnauthorizedException("Account is inactive")
        
        return user
    
    @staticmethod
    def create_tokens(user: User) -> dict:
        """Create access and refresh tokens for user."""
        token_data = {
            "sub": user.email,
            "user_id": str(user.id),
            "is_admin": user.is_admin,
        }
        
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }
