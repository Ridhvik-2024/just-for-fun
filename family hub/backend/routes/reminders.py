from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import SessionLocal
from backend.models import Reminder
from backend.schemas.reminders import ReminderCreate, ReminderOut
from backend.deps import get_current_user

router = APIRouter(prefix="/reminders", tags=["reminders"])
print("[ROUTES] reminders router loaded")

def get_db():
    print("[DB] Open session (reminders)")
    db = SessionLocal()
    try:
        yield db
    finally:
        print("[DB] Close session (reminders)")
        db.close()

@router.post("/", response_model=ReminderOut)
def create_reminder(
    data: ReminderCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    print("[REMINDERS] Create reminder:", data.title)
    reminder = Reminder(
        title=data.title,
        description=data.description,
        remind_at=data.remind_at,
        priority=data.priority,
        creator_id=user.id,
    )
    db.add(reminder)
    db.commit()
    db.refresh(reminder)
    return reminder

@router.get("/", response_model=list[ReminderOut])
def list_reminders(
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    print("[REMINDERS] List reminders")
    return (
        db.query(Reminder)
        .filter(Reminder.creator_id == user.id)
        .order_by(Reminder.remind_at.asc())
        .all()
    )

@router.post("/{reminder_id}/done")
def mark_done(
    reminder_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    print("[REMINDERS] Mark done:", reminder_id)
    reminder = (
        db.query(Reminder)
        .filter(Reminder.id == reminder_id, Reminder.creator_id == user.id)
        .first()
    )
    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")
    reminder.is_done = True
    db.commit()
    return {"status": "ok"}
