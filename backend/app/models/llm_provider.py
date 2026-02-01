from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, BigInteger, Text, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class LLMProviderConfig(Base):
    __tablename__ = "llm_providers"
    
    id = Column(Integer, primary_key=True)
    provider_name = Column(String(50), unique=True, nullable=False)
    is_active = Column(Boolean, default=True)
    priority = Column(Integer, default=0)
    requests_per_minute = Column(Integer, default=60)
    tokens_per_minute = Column(Integer, nullable=True)
    failure_threshold = Column(Integer, default=3)
    timeout_seconds = Column(Integer, default=60)
    
    api_keys = relationship("LLMAPIKey", back_populates="provider", cascade="all, delete-orphan")
    usage_logs = relationship("LLMUsageLog", back_populates="provider")
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class LLMAPIKey(Base):
    __tablename__ = "llm_api_keys"
    
    id = Column(Integer, primary_key=True)
    provider_id = Column(Integer, ForeignKey("llm_providers.id", ondelete="CASCADE"), nullable=False)
    key_name = Column(String(100), nullable=False)
    api_key_encrypted = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True)
    
    last_used_at = Column(DateTime, nullable=True)
    request_count = Column(BigInteger, default=0)
    failure_count = Column(Integer, default=0)
    last_failure_at = Column(DateTime, nullable=True)
    
    provider = relationship("LLMProviderConfig", back_populates="api_keys")
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_provider_active', 'provider_id', 'is_active'),
    )


class LLMUsageLog(Base):
    __tablename__ = "llm_usage_logs"
    
    id = Column(BigInteger, primary_key=True)
    provider_id = Column(Integer, ForeignKey("llm_providers.id", ondelete="SET NULL"), nullable=True)
    api_key_id = Column(Integer, ForeignKey("llm_api_keys.id", ondelete="SET NULL"), nullable=True)
    session_id = Column(String(100), nullable=False)
    
    request_tokens = Column(Integer, default=0)
    response_tokens = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    latency_ms = Column(Float, nullable=False)
    
    success = Column(Boolean, default=True)
    error_message = Column(Text, nullable=True)
    
    provider = relationship("LLMProviderConfig", back_populates="usage_logs")
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    __table_args__ = (
        Index('idx_session_created', 'session_id', 'created_at'),
        Index('idx_provider_success', 'provider_id', 'success', 'created_at'),
    )
