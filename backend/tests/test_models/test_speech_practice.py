import pytest
from datetime import datetime
from app.models.speech_practice import SpeechPracticeSession, UserProgressLLM
from sqlalchemy.orm import Session

def test_create_speech_practice_session(db: Session):
    session = SpeechPracticeSession(
        id="test-session-123",
        user_id="user-456",
        mode="conversation",
        audio_url="s3://bucket/audio.wav",
        transcript="Hello world",
        provider_used="openai"
    )
    db.add(session)
    db.commit()
    
    assert session.id == "test-session-123"
    assert session.mode == "conversation"
    assert session.transcript == "Hello world"

def test_create_user_progress_llm(db: Session):
    progress = UserProgressLLM(
        user_id="user-789",
        total_sessions=5,
        total_tokens_used=12345,
        average_score=8.5,
        last_practice_at=datetime.utcnow()
    )
    db.add(progress)
    db.commit()
    
    assert progress.id is not None
    assert progress.total_sessions == 5
    assert progress.average_score == 8.5

def test_speech_session_with_scores(db: Session):
    session = SpeechPracticeSession(
        id="test-session-456",
        user_id="user-123",
        mode="sentence_practice",
        overall_score=9.0,
        pronunciation_score=8.5,
        prosody_score=9.5,
        emotion_score=8.0
    )
    db.add(session)
    db.commit()
    
    assert session.overall_score == 9.0
    assert session.pronunciation_score == 8.5
