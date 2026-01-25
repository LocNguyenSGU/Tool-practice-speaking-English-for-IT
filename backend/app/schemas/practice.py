from datetime import datetime
from pydantic import BaseModel
from app.schemas.sentence import SentenceWithAudio


class PracticeRecordRequest(BaseModel):
    sentence_id: int


class PracticeProgressItem(BaseModel):
    sentence_id: int
    vi_text: str
    en_text: str
    practiced_count: int
    last_practiced_at: datetime
    
    class Config:
        from_attributes = True


class PracticeStats(BaseModel):
    total_practiced: int
    total_practice_count: int
    recent_practiced_count: int


class NextSentenceResponse(BaseModel):
    sentence: SentenceWithAudio
    progress: dict | None = None  # {"practiced_count": 3, "total_in_lesson": 50, ...}
