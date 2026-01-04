from pydantic import BaseModel
from datetime import datetime

class ChatMessageCreate(BaseModel):
    ciphertext: str
    iv: str

class ChatMessageOut(BaseModel):
    id: int
    sender_id: int
    ciphertext: str
    iv: str
    created_at: datetime

    class Config:
        from_attributes = True
