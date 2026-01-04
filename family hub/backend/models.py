from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, LargeBinary
from datetime import datetime

from backend.database import Base

print("[MODELS] Loading User model")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    print("[MODELS] Loading Notice and Reminder models")

class Notice(Base):
    __tablename__ = "notices"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(String, nullable=True)
    is_important = Column(Boolean, default=False)
    expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)


class Reminder(Base):
    __tablename__ = "reminders"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    remind_at = Column(DateTime, nullable=False)
    priority = Column(String, default="normal")  # low | normal | high
    is_done = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)

print("[MODELS] Loading ChatMessage model")

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    ciphertext = Column(LargeBinary, nullable=False)
    iv = Column(LargeBinary, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)