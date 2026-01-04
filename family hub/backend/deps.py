from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from backend.database import SessionLocal
from backend.models import User
from backend.auth import decode_access_token

print("[DEPS] deps.py loaded")

security = HTTPBearer()


def get_db():
    print("[DEPS] Opening DB session")
    db = SessionLocal()
    try:
        yield db
    finally:
        print("[DEPS] Closing DB session")
        db.close()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    print("[DEPS] get_current_user called")

    token = credentials.credentials
    payload = decode_access_token(token)

    username = payload.get("sub")
    if not username:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user



def require_admin(user: User = Depends(get_current_user)):
    print("[DEPS] require_admin check")
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user
