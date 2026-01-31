"""
Users Management Endpoints
"""
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.core.database import get_db
from app.core.exceptions import NotFoundException, BadRequestException
from app.core.security import get_password_hash
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserInDB
from app.schemas.common import PaginatedResponse, PaginationParams, PaginationMeta
from app.dependencies import get_current_admin, get_current_user

router = APIRouter()


@router.get("/users", response_model=PaginatedResponse[UserInDB])
async def get_users(
    pagination: PaginationParams = Depends(),
    search: str = Query(None, description="Search in email or username"),
    is_admin: Optional[bool] = Query(None, description="Filter by admin status"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    admin=Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """
    Get all users with pagination and search
    
    Requires: Admin authentication
    
    - **page**: Page number (default: 1)
    - **page_size**: Items per page (default: 10, max: 100)
    - **search**: Optional search query (email or username)
    - **is_admin**: Filter by admin status (true/false)
    - **is_active**: Filter by active status (true/false)
    """
    query = db.query(User)
    
    # Search filter
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                User.email.ilike(search_term),
                User.username.ilike(search_term)
            )
        )
    
    # Admin filter
    if is_admin is not None:
        query = query.filter(User.is_admin == is_admin)
    
    # Active filter
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    
    # Order by created_at desc
    query = query.order_by(User.created_at.desc())
    
    # Count total
    total = query.count()
    
    # Pagination
    offset = (pagination.page - 1) * pagination.limit
    items = query.offset(offset).limit(pagination.limit).all()
    
    # Calculate pagination meta
    total_pages = (total + pagination.limit - 1) // pagination.limit
    
    return PaginatedResponse(
        items=items,
        pagination=PaginationMeta(
            page=pagination.page,
            limit=pagination.limit,
            total_items=total,
            total_pages=total_pages,
            has_next=pagination.page < total_pages,
            has_prev=pagination.page > 1
        )
    )


@router.get("/users/{user_id}", response_model=UserInDB)
async def get_user(
    user_id: UUID,
    admin=Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """
    Get a specific user by ID
    
    Requires: Admin authentication
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise NotFoundException(f"User with id {user_id} not found")
    return user


@router.post("/users", response_model=UserInDB, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    admin=Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """
    Create a new user
    
    Requires: Admin authentication
    
    - **email**: User email (required, unique)
    - **username**: Username (required, unique)
    - **password**: Password (required)
    """
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise BadRequestException(f"Email {user_data.email} already registered")
    
    # Check if username already exists
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise BadRequestException(f"Username {user_data.username} already taken")
    
    # Create user
    hashed_password = get_password_hash(user_data.password)
    user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed_password,
        is_active=True,
        is_admin=False,
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.put("/users/{user_id}", response_model=UserInDB)
async def update_user(
    user_id: UUID,
    user_data: UserUpdate,
    admin=Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """
    Update a user
    
    Requires: Admin authentication
    
    - **is_active**: Active status (optional)
    - **is_admin**: Admin status (optional)
    - **password**: New password (optional)
    
    Note: Email and username cannot be changed
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise NotFoundException(f"User with id {user_id} not found")
    
    # Prevent admin from disabling themselves
    if user.id == admin.id and user_data.is_active is False:
        raise BadRequestException("You cannot deactivate your own account")
    
    # Prevent admin from removing their own admin rights
    if user.id == admin.id and user_data.is_admin is False:
        raise BadRequestException("You cannot remove your own admin rights")
    
    # Update fields (excluding email and username)
    update_data = user_data.model_dump(exclude_unset=True, exclude={'email', 'username'})
    
    # Handle password separately if provided
    if 'password' in update_data and update_data['password']:
        user.hashed_password = get_password_hash(update_data['password'])
        del update_data['password']
    
    for field, value in update_data.items():
        setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    return user


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: UUID,
    admin=Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """
    Delete a user
    
    Requires: Admin authentication
    
    Note: Cannot delete your own account
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise NotFoundException(f"User with id {user_id} not found")
    
    # Prevent admin from deleting themselves
    if user.id == admin.id:
        raise BadRequestException("You cannot delete your own account")
    
    db.delete(user)
    db.commit()
    return None


@router.patch("/users/{user_id}/password", response_model=UserInDB)
async def update_user_password(
    user_id: UUID,
    password: str = Query(..., min_length=6, description="New password"),
    admin=Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """
    Update user password
    
    Requires: Admin authentication
    
    - **password**: New password (min 6 characters)
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise NotFoundException(f"User with id {user_id} not found")
    
    # Update password
    user.hashed_password = get_password_hash(password)
    
    db.commit()
    db.refresh(user)
    return user


@router.get("/users/stats/summary")
async def get_users_stats(
    admin=Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """
    Get user statistics
    
    Requires: Admin authentication
    
    Returns counts of total, active, inactive, and admin users
    """
    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.is_active == True).count()
    inactive_users = db.query(User).filter(User.is_active == False).count()
    admin_users = db.query(User).filter(User.is_admin == True).count()
    
    return {
        "total_users": total_users,
        "active_users": active_users,
        "inactive_users": inactive_users,
        "admin_users": admin_users,
    }
