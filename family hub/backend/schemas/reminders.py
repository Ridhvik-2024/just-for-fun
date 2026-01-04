from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ReminderCreate(BaseModel):
    title: str
    description: Optional[str] = None
    remind_at: datetime
    priority: str = "normal"  # low | normal | high

class ReminderOut(BaseModel):
    id: int
    title: str
    description: Optional[str]
    remind_at: datetime
    priority: str
    is_done: bool
    created_at: datetime

    class Config:
        from_attributes = True
