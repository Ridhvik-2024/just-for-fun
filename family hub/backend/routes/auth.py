from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.schemas.auth import LoginRequest, TokenResponse
from backend.database import SessionLocal
from backend.models import User
from backend.auth import verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])
print("[ROUTES] auth router loaded")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    print("[AUTH] Login attempt for:", data.username)
    user = db.query(User).filter(User.username == data.username).first()
    if not user or not verify_password(data.password, user.password_hash):
        print("[AUTH][ERROR] Invalid credentials")
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": user.username})
    print("[AUTH] Login success")
    return {"access_token": token}
