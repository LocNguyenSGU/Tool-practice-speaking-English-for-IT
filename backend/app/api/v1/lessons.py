"""
Lessons Endpoints
"""
from typing import List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db
from app.core.exceptions import NotFoundException, BadRequestException
from app.models.lesson import Lesson
from app.models.sentence import Sentence
from app.schemas.lesson import LessonCreate, LessonUpdate, LessonInDB
from app.schemas.common import PaginatedResponse, PaginationParams, PaginationMeta
from app.dependencies import get_current_admin, get_optional_user

router = APIRouter()


@router.get("/lessons", response_model=PaginatedResponse[LessonInDB])
async def get_lessons(
    pagination: PaginationParams = Depends(),
    search: str = Query(None, description="Search in title or description"),
    user=Depends(get_optional_user),
    db: Session = Depends(get_db),
):
    """
    Get all lessons with pagination and search
    
    - **page**: Page number (default: 1)
    - **page_size**: Items per page (default: 10, max: 100)
    - **search**: Optional search query
    
    Public endpoint (guest + registered users)
    """
    query = db.query(Lesson)
    
    # Search filter
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Lesson.title.ilike(search_term)) | (Lesson.description.ilike(search_term))
        )
    
    # Order by order_index
    query = query.order_by(Lesson.order_index)
    
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


@router.get("/lessons/{lesson_id}", response_model=LessonInDB)
async def get_lesson(
    lesson_id: int,
    user=Depends(get_optional_user),
    db: Session = Depends(get_db),
):
    """
    Get a specific lesson by ID
    
    Public endpoint (guest + registered users)
    """
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        raise NotFoundException(f"Lesson with id {lesson_id} not found")
    return lesson


@router.post("/lessons", response_model=LessonInDB, status_code=status.HTTP_201_CREATED)
async def create_lesson(
    lesson_data: LessonCreate,
    admin=Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """
    Create a new lesson
    
    Requires: Admin authentication
    
    - **title**: Lesson title (required)
    - **description**: Lesson description (optional)
    - **order_index**: Display order (default: max + 1)
    """
    # Auto-increment order_index if not provided
    if lesson_data.order_index is None:
        max_order = db.query(func.max(Lesson.order_index)).scalar() or 0
        lesson_data.order_index = max_order + 1
    
    lesson = Lesson(**lesson_data.model_dump())
    db.add(lesson)
    db.commit()
    db.refresh(lesson)
    return lesson


@router.put("/lessons/{lesson_id}", response_model=LessonInDB)
async def update_lesson(
    lesson_id: int,
    lesson_data: LessonUpdate,
    admin=Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """
    Update a lesson
    
    Requires: Admin authentication
    """
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        raise NotFoundException(f"Lesson with id {lesson_id} not found")
    
    # Update fields
    update_data = lesson_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(lesson, field, value)
    
    db.commit()
    db.refresh(lesson)
    return lesson


@router.delete("/lessons/{lesson_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_lesson(
    lesson_id: int,
    admin=Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """
    Delete a lesson
    
    Requires: Admin authentication
    
    Note: This will also delete all associated sentences (cascade)
    """
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        raise NotFoundException(f"Lesson with id {lesson_id} not found")
    
    db.delete(lesson)
    db.commit()
    return None


@router.get("/lessons/{lesson_id}/sentences-count")
async def get_lesson_sentences_count(
    lesson_id: int,
    user=Depends(get_optional_user),
    db: Session = Depends(get_db),
):
    """
    Get count of sentences in a lesson
    
    Public endpoint (guest + registered users)
    """
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        raise NotFoundException(f"Lesson with id {lesson_id} not found")
    
    count = db.query(Sentence).filter(Sentence.lesson_id == lesson_id).count()
    return {"lesson_id": lesson_id, "sentences_count": count}
