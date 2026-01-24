"""
Practice Endpoints
"""
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.exceptions import NotFoundException
from app.models.sentence import Sentence
from app.schemas.practice import (
    NextSentenceResponse,
    PracticeRecordRequest,
    PracticeStats,
)
from app.services.practice_service import PracticeService
from app.dependencies import get_optional_user

router = APIRouter()


@router.get("/practice/next", response_model=NextSentenceResponse)
async def get_next_sentence(
    lesson_id: int = Query(None, description="Filter by lesson ID"),
    user=Depends(get_optional_user),
    db: Session = Depends(get_db),
):
    """
    Get next sentence for practice
    
    Smart selection algorithm:
    - For authenticated users: Returns least practiced sentence (excluding recently practiced < 5 min)
    - For guests: Returns random sentence
    
    - **lesson_id**: Optional lesson filter
    
    Public endpoint (guest + registered users)
    """
    result = PracticeService.get_next_sentence(db, user, lesson_id)
    if not result:
        raise NotFoundException("No sentences available for practice")
    
    return result


@router.post("/practice/record", status_code=status.HTTP_201_CREATED)
async def record_practice(
    request: PracticeRecordRequest,
    user=Depends(get_optional_user),
    db: Session = Depends(get_db),
):
    """
    Record a practice session
    
    For authenticated users: Updates progress tracking
    For guests: No-op (returns success but doesn't save)
    
    - **sentence_id**: Sentence that was practiced
    
    Public endpoint (guest + registered users)
    """
    # Check sentence exists
    sentence = db.query(Sentence).filter(Sentence.id == request.sentence_id).first()
    if not sentence:
        raise NotFoundException(f"Sentence with id {request.sentence_id} not found")
    
    # Record practice (only for authenticated users)
    if user:
        PracticeService.record_practice(db, user.id, request.sentence_id)
        message = "Practice recorded successfully"
    else:
        message = "Practice completed (not recorded for guest)"
    
    return {"message": message, "sentence_id": request.sentence_id}


@router.get("/practice/stats", response_model=PracticeStats)
async def get_practice_stats(
    lesson_id: int = Query(None, description="Filter by lesson ID"),
    user=Depends(get_optional_user),
    db: Session = Depends(get_db),
):
    """
    Get practice statistics for authenticated user
    
    Returns:
    - **total_practiced**: Total number of sentences practiced
    - **total_practice_count**: Total practice sessions
    - **lesson_stats**: Per-lesson breakdown (if lesson_id provided)
    
    Requires: Authentication (guests will get 401)
    """
    from app.core.exceptions import UnauthorizedException
    from app.models.progress import Progress
    from sqlalchemy import func
    
    if not user:
        raise UnauthorizedException("Authentication required for statistics")
    
    # Base query
    query = db.query(Progress).filter(Progress.user_id == user.id)
    
    # Lesson filter
    if lesson_id is not None:
        query = query.join(Sentence).filter(Sentence.lesson_id == lesson_id)
    
    # Count stats
    total_practiced = query.count()
    total_practice_count = query.with_entities(func.sum(Progress.practiced_count)).scalar() or 0
    
    # Recent activity (last 7 days)
    from datetime import datetime, timedelta
    week_ago = datetime.utcnow() - timedelta(days=7)
    recent_count = (
        query.filter(Progress.last_practiced_at >= week_ago).count()
    )
    
    return PracticeStats(
        total_practiced=total_practiced,
        total_practice_count=int(total_practice_count),
        recent_practiced_count=recent_count,
    )
