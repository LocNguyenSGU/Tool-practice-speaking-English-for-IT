"""
Sentences Endpoints
"""
from typing import List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db
from app.core.exceptions import NotFoundException, BadRequestException
from app.models.lesson import Lesson
from app.models.sentence import Sentence
from app.schemas.sentence import (
    SentenceCreate,
    SentenceUpdate,
    SentenceInDB,
    SentenceWithAudio,
    BulkSentenceCreate,
)
from app.schemas.common import PaginatedResponse, PaginationParams
from app.dependencies import get_current_admin, get_optional_user

router = APIRouter()


@router.get("/sentences", response_model=PaginatedResponse[SentenceWithAudio])
async def get_sentences(
    pagination: PaginationParams = Depends(),
    lesson_id: int = Query(None, description="Filter by lesson ID"),
    search: str = Query(None, description="Search in Vietnamese or English text"),
    user=Depends(get_optional_user),
    db: Session = Depends(get_db),
):
    """
    Get all sentences with pagination, filtering, and search
    
    - **page**: Page number (default: 1)
    - **page_size**: Items per page (default: 10, max: 100)
    - **lesson_id**: Filter by specific lesson (optional)
    - **search**: Search query (optional)
    
    Public endpoint (guest + registered users)
    """
    query = db.query(Sentence)
    
    # Lesson filter
    if lesson_id is not None:
        query = query.filter(Sentence.lesson_id == lesson_id)
    
    # Search filter
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Sentence.vi_text.ilike(search_term)) | (Sentence.en_text.ilike(search_term))
        )
    
    # Order by lesson and order_index
    query = query.order_by(Sentence.lesson_id, Sentence.order_index)
    
    # Count total
    total = query.count()
    
    # Pagination
    offset = (pagination.page - 1) * pagination.page_size
    items = query.offset(offset).limit(pagination.page_size).all()
    
    # Convert to SentenceWithAudio
    from app.services.tts_service import TTSService
    result = []
    for sentence in items:
        audio_vi = None
        audio_en = None
        
        # Check if audio files exist
        for audio_file in sentence.audio_files:
            path = TTSService.get_audio_path(sentence.id, audio_file.language)
            if audio_file.language == "vi":
                audio_vi = f"/api/v1/audio/{sentence.id}/vi"
            elif audio_file.language == "en":
                audio_en = f"/api/v1/audio/{sentence.id}/en"
        
        result.append(
            SentenceWithAudio(
                **sentence.__dict__,
                audio_vi=audio_vi,
                audio_en=audio_en,
            )
        )
    
    return PaginatedResponse.create(result, total, pagination.page, pagination.page_size)


@router.get("/sentences/{sentence_id}", response_model=SentenceWithAudio)
async def get_sentence(
    sentence_id: int,
    user=Depends(get_optional_user),
    db: Session = Depends(get_db),
):
    """
    Get a specific sentence by ID
    
    Public endpoint (guest + registered users)
    """
    sentence = db.query(Sentence).filter(Sentence.id == sentence_id).first()
    if not sentence:
        raise NotFoundException(f"Sentence with id {sentence_id} not found")
    
    # Get audio URLs
    from app.services.tts_service import TTSService
    audio_vi = None
    audio_en = None
    
    for audio_file in sentence.audio_files:
        if audio_file.language == "vi":
            audio_vi = f"/api/v1/audio/{sentence.id}/vi"
        elif audio_file.language == "en":
            audio_en = f"/api/v1/audio/{sentence.id}/en"
    
    return SentenceWithAudio(
        **sentence.__dict__,
        audio_vi=audio_vi,
        audio_en=audio_en,
    )


@router.post("/sentences", response_model=SentenceInDB, status_code=status.HTTP_201_CREATED)
async def create_sentence(
    sentence_data: SentenceCreate,
    admin=Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """
    Create a new sentence
    
    Requires: Admin authentication
    
    - **lesson_id**: Lesson ID (required)
    - **vi_text**: Vietnamese text (required)
    - **en_text**: English text (required)
    - **order_index**: Display order (default: max + 1 for lesson)
    """
    # Check lesson exists
    lesson = db.query(Lesson).filter(Lesson.id == sentence_data.lesson_id).first()
    if not lesson:
        raise NotFoundException(f"Lesson with id {sentence_data.lesson_id} not found")
    
    # Auto-increment order_index if not provided
    if sentence_data.order_index is None:
        max_order = (
            db.query(func.max(Sentence.order_index))
            .filter(Sentence.lesson_id == sentence_data.lesson_id)
            .scalar() or 0
        )
        sentence_data.order_index = max_order + 1
    
    sentence = Sentence(**sentence_data.model_dump())
    db.add(sentence)
    db.commit()
    db.refresh(sentence)
    return sentence


@router.post("/sentences/bulk", response_model=List[SentenceInDB], status_code=status.HTTP_201_CREATED)
async def bulk_create_sentences(
    bulk_data: BulkSentenceCreate,
    admin=Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """
    Bulk create sentences for a lesson
    
    Requires: Admin authentication
    
    - **lesson_id**: Lesson ID (required)
    - **sentences**: List of sentences with vi_text and en_text
    """
    # Check lesson exists
    lesson = db.query(Lesson).filter(Lesson.id == bulk_data.lesson_id).first()
    if not lesson:
        raise NotFoundException(f"Lesson with id {bulk_data.lesson_id} not found")
    
    # Get current max order_index
    max_order = (
        db.query(func.max(Sentence.order_index))
        .filter(Sentence.lesson_id == bulk_data.lesson_id)
        .scalar() or 0
    )
    
    # Create sentences
    created_sentences = []
    for idx, sentence_data in enumerate(bulk_data.sentences):
        sentence = Sentence(
            lesson_id=bulk_data.lesson_id,
            vi_text=sentence_data.vi_text,
            en_text=sentence_data.en_text,
            order_index=max_order + idx + 1,
        )
        db.add(sentence)
        created_sentences.append(sentence)
    
    db.commit()
    for sentence in created_sentences:
        db.refresh(sentence)
    
    return created_sentences


@router.put("/sentences/{sentence_id}", response_model=SentenceInDB)
async def update_sentence(
    sentence_id: int,
    sentence_data: SentenceUpdate,
    admin=Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """
    Update a sentence
    
    Requires: Admin authentication
    """
    sentence = db.query(Sentence).filter(Sentence.id == sentence_id).first()
    if not sentence:
        raise NotFoundException(f"Sentence with id {sentence_id} not found")
    
    # Update fields
    update_data = sentence_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(sentence, field, value)
    
    db.commit()
    db.refresh(sentence)
    
    # Delete cached audio files if text changed
    if "vi_text" in update_data or "en_text" in update_data:
        from app.services.tts_service import TTSService
        TTSService.delete_audio(sentence_id)
    
    return sentence


@router.delete("/sentences/{sentence_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_sentence(
    sentence_id: int,
    admin=Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """
    Delete a sentence
    
    Requires: Admin authentication
    
    Note: This will also delete associated audio files
    """
    sentence = db.query(Sentence).filter(Sentence.id == sentence_id).first()
    if not sentence:
        raise NotFoundException(f"Sentence with id {sentence_id} not found")
    
    # Delete audio files
    from app.services.tts_service import TTSService
    TTSService.delete_audio(sentence_id)
    
    db.delete(sentence)
    db.commit()
    return None
