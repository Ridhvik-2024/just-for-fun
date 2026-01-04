from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class NoticeCreate(BaseModel):
    title: str
    content: Optional[str] = None
    is_important: bool = False
    expires_at: Optional[datetime] = None

class NoticeOut(BaseModel):
    id: int
    title: str
    content: Optional[str]
    is_important: bool
    expires_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True
