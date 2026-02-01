from sqlalchemy import Column, Integer, String, Float, Text, DateTime, BigInteger, Boolean, JSON, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class SpeechPracticeSession(Base):
    __tablename__ = "speech_practice_sessions"
    
    id = Column(String(100), primary_key=True)
    user_id = Column(String(36), nullable=False, index=True)
    mode = Column(String(50), nullable=False)  # "conversation" or "sentence_practice"
    
    # Audio data
    audio_url = Column(String(512), nullable=True)
    audio_duration_ms = Column(Integer, nullable=True)
    
    # Transcription
    transcript = Column(Text, nullable=True)
    reference_text = Column(Text, nullable=True)  # For sentence practice mode
    
    # Prosody analysis
    prosody_features = Column(JSON, nullable=True)  # {pitch, energy, rate, pauses}
    
    # LLM analysis results
    provider_used = Column(String(50), nullable=True)
    llm_response = Column(JSON, nullable=True)
    
    # Scores (0-10 scale)
    overall_score = Column(Float, nullable=True)
    pronunciation_score = Column(Float, nullable=True)
    prosody_score = Column(Float, nullable=True)
    emotion_score = Column(Float, nullable=True)
    confidence_score = Column(Float, nullable=True)
    fluency_score = Column(Float, nullable=True)
    
    # Feedback
    conversational_feedback = Column(Text, nullable=True)
    detailed_feedback = Column(JSON, nullable=True)
    
    # Performance metrics
    total_latency_ms = Column(Integer, nullable=True)
    stt_latency_ms = Column(Integer, nullable=True)
    prosody_latency_ms = Column(Integer, nullable=True)
    llm_latency_ms = Column(Integer, nullable=True)
    
    # Status tracking
    status = Column(String(20), default="processing")  # processing, completed, failed
    error_message = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    completed_at = Column(DateTime, nullable=True)
    
    __table_args__ = (
        Index('idx_user_status_created', 'user_id', 'status', 'created_at'),
        Index('idx_mode_created', 'mode', 'created_at'),
    )


class UserProgressLLM(Base):
    __tablename__ = "user_progress_llm"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String(36), unique=True, nullable=False, index=True)
    
    # Session statistics
    total_sessions = Column(Integer, default=0)
    conversation_sessions = Column(Integer, default=0)
    sentence_practice_sessions = Column(Integer, default=0)
    
    # Score averages
    average_score = Column(Float, nullable=True)
    average_pronunciation = Column(Float, nullable=True)
    average_prosody = Column(Float, nullable=True)
    average_emotion = Column(Float, nullable=True)
    average_confidence = Column(Float, nullable=True)
    average_fluency = Column(Float, nullable=True)
    
    # Usage statistics
    total_audio_duration_ms = Column(BigInteger, default=0)
    total_tokens_used = Column(BigInteger, default=0)
    
    # Streaks and engagement
    current_streak_days = Column(Integer, default=0)
    longest_streak_days = Column(Integer, default=0)
    last_practice_at = Column(DateTime, nullable=True)
    
    # Performance trends (last 7 days)
    recent_scores = Column(JSON, nullable=True)  # Array of recent scores for trending
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
