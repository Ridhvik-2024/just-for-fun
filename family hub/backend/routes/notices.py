from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime

from backend.database import SessionLocal
from backend.models import Notice
from backend.schemas.notices import NoticeCreate, NoticeOut
from backend.deps import get_current_user

router = APIRouter(prefix="/notices", tags=["notices"])
print("[ROUTES] notices router loaded")

def get_db():
    print("[DB] Open session (notices)")
    db = SessionLocal()
    try:
        yield db
    finally:
        print("[DB] Close session (notices)")
        db.close()

@router.post("/", response_model=NoticeOut)
def create_notice(
    data: NoticeCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    print("[NOTICES] Create notice:", data.title)
    notice = Notice(
        title=data.title,
        content=data.content,
        is_important=data.is_important,
        expires_at=data.expires_at,
        creator_id=user.id,
    )
    db.add(notice)
    db.commit()
    db.refresh(notice)
    return notice

@router.get("/", response_model=list[NoticeOut])
def list_notices(
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    print("[NOTICES] List notices")
    now = datetime.utcnow()
    return (
        db.query(Notice)
        .filter(
            (Notice.expires_at == None) | (Notice.expires_at > now)
        )
        .order_by(Notice.is_important.desc(), Notice.created_at.desc())
        .all()
    )
