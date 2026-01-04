from fastapi import APIRouter, Depends, Query, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from datetime import datetime
import base64

from backend.database import SessionLocal
from backend.ws_manager import ConnectionManager
from backend.auth import decode_access_token
from backend.models import ChatMessage
from backend.schemas.chat import ChatMessageCreate, ChatMessageOut
from backend.deps import get_current_user

router = APIRouter(prefix="/chat", tags=["chat"])
print("[ROUTES] chat router loaded")

MAX_MESSAGES = 50
manager = ConnectionManager()


# --------------------------------------------------
# DB dependency
# --------------------------------------------------
def get_db():
    print("[DB] Open session (chat)")
    db = SessionLocal()
    try:
        yield db
    finally:
        print("[DB] Close session (chat)")
        db.close()


# --------------------------------------------------
# REST: Send message (optional, still works)
# --------------------------------------------------
@router.post("/", response_model=ChatMessageOut)
def send_message(
    data: ChatMessageCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    print("[CHAT] Storing encrypted message from user:", user.id)

    msg = ChatMessage(
        sender_id=user.id,
        ciphertext=base64.b64decode(data.ciphertext),
        iv=base64.b64decode(data.iv),
    )

    db.add(msg)
    db.commit()
    db.refresh(msg)

    print("[CHAT] Message stored, returning response")

    return {
        "id": msg.id,
        "sender_id": msg.sender_id,
        "ciphertext": base64.b64encode(msg.ciphertext).decode(),
        "iv": base64.b64encode(msg.iv).decode(),
        "created_at": msg.created_at,
    }


# --------------------------------------------------
# REST: Fetch message history
# --------------------------------------------------
@router.get("/", response_model=list[ChatMessageOut])
def get_messages(
    since: datetime | None = Query(None),
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    print("[CHAT] Fetch messages since:", since)

    query = db.query(ChatMessage)

    if since:
        query = query.filter(ChatMessage.created_at > since)

    messages = (
        query
        .order_by(ChatMessage.created_at.asc())
        .limit(MAX_MESSAGES)
        .all()
    )

    print(f"[CHAT] Returning {len(messages)} messages")

    return [
        {
            "id": m.id,
            "sender_id": m.sender_id,
            "ciphertext": base64.b64encode(m.ciphertext).decode(),
            "iv": base64.b64encode(m.iv).decode(),
            "created_at": m.created_at,
        }
        for m in messages
    ]


# --------------------------------------------------
# WEBSOCKET: Persistent + broadcast chat (Phase 7.1)
# --------------------------------------------------
@router.websocket("/ws/chat")
async def chat_ws(websocket: WebSocket):
    print("[WS] Incoming WebSocket connection")

    token = websocket.query_params.get("token")
    if not token:
        print("[WS] No token provided")
        await websocket.close(code=1008)
        return

    try:
        payload = decode_access_token(token)
        username = payload.get("sub")
        print("[WS] Authenticated user:", username)
    except Exception:
        print("[WS] Invalid token")
        await websocket.close(code=1008)
        return

    await manager.connect(websocket)

    db = SessionLocal()

    try:
        while True:
            data = await websocket.receive_json()
            print("[WS] Message received")

            # ---- Persist encrypted message ----
            msg = ChatMessage(
                sender_id=1,  # TEMP: fixed properly in Phase 7.2
                ciphertext=base64.b64decode(data["ciphertext"]),
                iv=base64.b64decode(data["iv"]),
            )

            db.add(msg)
            db.commit()
            db.refresh(msg)

            print("[WS] Message stored with ID:", msg.id)

            # ---- Broadcast canonical payload ----
            payload = {
            "id": msg.id,
            "sender": username,   # 👈 ADD THIS
            "ciphertext": base64.b64encode(msg.ciphertext).decode(),
            "iv": base64.b64encode(msg.iv).decode(),
            "created_at": msg.created_at.isoformat(),
        }


            await manager.broadcast(payload)
            print("[WS] Message broadcasted")

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print("[WS] Client disconnected")
    finally:
        db.close()
        print("[DB] Session closed (ws)")
