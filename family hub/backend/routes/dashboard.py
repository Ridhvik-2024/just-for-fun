from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, date, timedelta

from backend.database import SessionLocal
from backend.models import Notice, Reminder
from backend.deps import get_current_user

router = APIRouter(prefix="/dashboard", tags=["dashboard"])
print("[ROUTES] dashboard router loaded")


def get_db():
    print("[DB] Open session (dashboard)")
    db = SessionLocal()
    try:
        yield db
    finally:
        print("[DB] Close session (dashboard)")
        db.close()


@router.get("/")
def get_dashboard(
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    print("[DASHBOARD] Fetching dashboard data")

    now = datetime.utcnow()
    today_start = datetime.combine(date.today(), datetime.min.time())
    today_end = today_start + timedelta(days=1)

    # Important & active notices
    notices = (
        db.query(Notice)
        .filter(
            (Notice.expires_at == None) | (Notice.expires_at > now)
        )
        .order_by(Notice.is_important.desc(), Notice.created_at.desc())
        .limit(5)
        .all()
    )

    # Today's reminders
    todays_reminders = (
        db.query(Reminder)
        .filter(
            Reminder.creator_id == user.id,
            Reminder.remind_at >= today_start,
            Reminder.remind_at < today_end,
            Reminder.is_done == False,
        )
        .order_by(Reminder.remind_at.asc())
        .all()
    )

    # Upcoming reminders (next 7 days, excluding today)
    upcoming_reminders = (
        db.query(Reminder)
        .filter(
            Reminder.creator_id == user.id,
            Reminder.remind_at >= today_end,
            Reminder.remind_at < today_end + timedelta(days=7),
            Reminder.is_done == False,
        )
        .order_by(Reminder.remind_at.asc())
        .all()
    )

    return {
        "notices": notices,
        "today": todays_reminders,
        "upcoming": upcoming_reminders,
    }
