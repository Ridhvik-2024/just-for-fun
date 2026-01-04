from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext

print("[AUTH] auth.py loaded")

# --- CONFIG ---
SECRET_KEY = "CHANGE_ME_TO_A_RANDOM_SECRET"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    print("[AUTH] Hashing password")
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    print("[AUTH] Verifying password")
    return pwd_context.verify(password, password_hash)


def create_access_token(data: dict, expires_minutes: int = ACCESS_TOKEN_EXPIRE_MINUTES) -> str:
    print("[AUTH] Creating access token")
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=expires_minutes)
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token


def decode_access_token(token: str) -> dict:
    print("[AUTH] Decoding access token")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        print("[AUTH][ERROR] Invalid token:", e)
        raise
