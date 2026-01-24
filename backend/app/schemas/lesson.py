from datetime import datetime
from pydantic import BaseModel


class LessonBase(BaseModel):
    title: str
    description: str | None = None
    order_index: int = 0
    is_active: bool = True


class LessonCreate(LessonBase):
    pass


class LessonUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    order_index: int | None = None
    is_active: bool | None = None


class LessonInDB(LessonBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
