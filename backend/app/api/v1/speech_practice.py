from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import uuid

from app.dependencies import get_db, get_current_user
from app.models.speech_practice import SpeechPracticeSession
from app.models.user import User
from app.schemas.common import MessageResponse
from pydantic import BaseModel, Field


# Schemas
class SessionCreate(BaseModel):
    mode: str = Field(..., pattern="^(conversation|sentence_practice)$")
    reference_text: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "mode": "conversation",
                "reference_text": None
            }
        }


class SessionResponse(BaseModel):
    id: str
    user_id: str
    mode: str
    status: str
    reference_text: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class SessionListResponse(BaseModel):
    sessions: List[SessionResponse]
    total: int


class SessionResultsUpdate(BaseModel):
    transcript: str
    scores: dict
    feedback: dict
    prosody_features: Optional[dict] = None


# Router
router = APIRouter(prefix="/speech-practice", tags=["Speech Practice"])


@router.post("/sessions", response_model=SessionResponse, status_code=status.HTTP_200_OK)
async def create_session(
    session_data: SessionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new speech practice session
    
    Modes:
    - conversation: Free-form conversation practice
    - sentence_practice: Practice specific sentences with reference text
    """
    session = SpeechPracticeSession(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        mode=session_data.mode,
        reference_text=session_data.reference_text,
        status="in_progress"
    )
    
    db.add(session)
    db.commit()
    db.refresh(session)
    
    return session


@router.get("/sessions", response_model=SessionListResponse)
async def list_sessions(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List all speech practice sessions for the current user
    """
    sessions = db.query(SpeechPracticeSession).filter(
        SpeechPracticeSession.user_id == current_user.id
    ).order_by(
        SpeechPracticeSession.created_at.desc()
    ).offset(skip).limit(limit).all()
    
    total = db.query(SpeechPracticeSession).filter(
        SpeechPracticeSession.user_id == current_user.id
    ).count()
    
    return SessionListResponse(sessions=sessions, total=total)


@router.get("/sessions/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get details of a specific speech practice session
    """
    session = db.query(SpeechPracticeSession).filter(
        SpeechPracticeSession.id == session_id,
        SpeechPracticeSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    return session


@router.put("/sessions/{session_id}/results", response_model=SessionResponse)
async def update_session_results(
    session_id: str,
    results: SessionResultsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a session with processing results (transcript, scores, feedback)
    """
    session = db.query(SpeechPracticeSession).filter(
        SpeechPracticeSession.id == session_id,
        SpeechPracticeSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    # Update session with results
    session.transcript = results.transcript
    session.overall_score = results.scores.get("overall")
    session.pronunciation_score = results.scores.get("pronunciation")
    session.prosody_score = results.scores.get("prosody")
    session.emotion_score = results.scores.get("emotion")
    session.confidence_score = results.scores.get("confidence")
    session.fluency_score = results.scores.get("fluency")
    session.detailed_feedback = results.feedback
    session.prosody_features = results.prosody_features
    session.status = "completed"
    session.completed_at = datetime.utcnow()
    
    db.commit()
    db.refresh(session)
    
    return session


@router.delete("/sessions/{session_id}", response_model=MessageResponse)
async def delete_session(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a speech practice session
    """
    session = db.query(SpeechPracticeSession).filter(
        SpeechPracticeSession.id == session_id,
        SpeechPracticeSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    db.delete(session)
    db.commit()
    
    return MessageResponse(message=f"Session {session_id} deleted successfully")
