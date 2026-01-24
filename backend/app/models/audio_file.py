from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class AudioFile(Base):
    __tablename__ = "audio_files"
    
    id = Column(Integer, primary_key=True, index=True)
    sentence_id = Column(Integer, ForeignKey("sentences.id", ondelete="CASCADE"), nullable=False, index=True)
    language = Column(String(2), nullable=False)  # 'vi' or 'en'
    file_path = Column(String(512), unique=True, nullable=False)
    file_size = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    sentence = relationship("Sentence", back_populates="audio_files")
    
    __table_args__ = (
        UniqueConstraint('sentence_id', 'language', name='uix_sentence_language'),
    )
