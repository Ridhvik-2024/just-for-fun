from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# Local imports
from backend.database import engine
from backend.models import Base
from backend.routes.auth import router as auth_router
from backend.routes.users import router as users_router
from backend.routes.notices import router as notices_router
from backend.routes.reminders import router as reminders_router
from backend.routes.dashboard import router as dashboard_router
from backend.routes.chat import router as chat_router

print("[MAIN] main.py module loaded")



# --------------------------------------------------
# Lifespan handler (startup / shutdown)
# --------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    # ---------- STARTUP ----------
    print("[LIFESPAN] Startup sequence begin")

    try:
        print("[DB] Creating database tables (if not exist)")
        Base.metadata.create_all(bind=engine)
        print("[DB] Database tables ready")
    except Exception as e:
        print("[DB][ERROR] Failed to create tables:", e)
        raise

    yield  # Application runs here

    # ---------- SHUTDOWN ----------
    print("[LIFESPAN] Shutdown sequence begin")


# --------------------------------------------------
# FastAPI app
# --------------------------------------------------
app = FastAPI(
    title="Family Hub",
    description="Private family hub backend",
    version="0.1.0",
    lifespan=lifespan,
)



# --------------------------------------------------
# Middleware
# --------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

print("[MAIN] FastAPI app created")

print("[MAIN] Including routers")
app.include_router(auth_router)
app.include_router(users_router)

app.include_router(notices_router)
app.include_router(reminders_router)

print("[MAIN] Notices & Reminders routers included")

app.include_router(chat_router)
print("[MAIN] Chat router included")

app.include_router(dashboard_router)
print("[MAIN] Dashboard router included")


# --------------------------------------------------
# Routes
# --------------------------------------------------
@app.get("/")
def root():
    print("[API] Root endpoint called")
    return {
        "status": "Family Hub backend running",
        "phase": 1,
    }
