from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.schemas.users import CreateUserRequest
from backend.database import SessionLocal
from backend.models import User
from backend.auth import hash_password
from backend.deps import require_admin

router = APIRouter(prefix="/users", tags=["users"])
print("[ROUTES] users router loaded")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/")
def create_user(
    data: CreateUserRequest,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    print("[USERS] Create user request:", data.username)
    if db.query(User).filter(User.username == data.username).first():
        raise HTTPException(status_code=400, detail="Username already exists")

    user = User(
        username=data.username,
        password_hash=hash_password(data.password),
        role=data.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    print("[USERS] User created:", user.username)
    return {"id": user.id, "username": user.username, "role": user.role}
