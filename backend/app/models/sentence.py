from sqlalchemy import Column, Integer, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Sentence(Base):
    __tablename__ = "sentences"
    
    id = Column(Integer, primary_key=True, index=True)
    lesson_id = Column(Integer, ForeignKey("lessons.id", ondelete="CASCADE"), nullable=False, index=True)
    vi_text = Column(Text, nullable=False)
    en_text = Column(Text, nullable=False)
    order_index = Column(Integer, default=0, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    lesson = relationship("Lesson", back_populates="sentences")
    audio_files = relationship("AudioFile", back_populates="sentence", cascade="all, delete-orphan")
