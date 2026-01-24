from datetime import datetime
from pydantic import BaseModel


class SentenceBase(BaseModel):
    lesson_id: int
    vi_text: str
    en_text: str
    order_index: int = 0


class SentenceCreate(SentenceBase):
    pass


class SentenceUpdate(BaseModel):
    lesson_id: int | None = None
    vi_text: str | None = None
    en_text: str | None = None
    order_index: int | None = None


class SentenceInDB(SentenceBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class SentenceWithAudio(SentenceInDB):
    vi_audio_url: str
    en_audio_url: str


class BulkSentenceCreate(BaseModel):
    lesson_id: int
    sentences: list[dict]  # [{"vi": "...", "en": "..."}]
