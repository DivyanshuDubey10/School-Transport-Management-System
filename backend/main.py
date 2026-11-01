import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env in the backend directory
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))

# Ensure the backend directory is importable as a root package
sys.path.insert(0, os.path.dirname(__file__))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import database
from routers import auth, students, parents, buses, routes, attendance, dashboard, requests, tracking

app = FastAPI(
    title="NeoYatra — School Transport Management API",
    version="1.0.0",
    description="Production FastAPI backend for NeoYatra school transport management system.",
)

# ---------------------------------------------------------------------------
# CORS Configuration (Configurable via ALLOWED_ORIGINS env variable)
# ---------------------------------------------------------------------------
raw_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,*")
allowed_origins = [orig.strip() for orig in raw_origins.split(",") if orig.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    """Ensure database schema and default admin exist on boot."""
    try:
        database.initialize_database()
        print("INFO: Database schema verified and initialized.")
    except Exception as e:
        print(f"WARNING: Could not auto-initialize database on startup: {e}")


# ---------------------------------------------------------------------------
# Routers — all grouped under /api/v1/
# ---------------------------------------------------------------------------
API_PREFIX = "/api/v1"

app.include_router(auth.router, prefix=API_PREFIX)
app.include_router(dashboard.router, prefix=API_PREFIX)
app.include_router(students.router, prefix=API_PREFIX)
app.include_router(parents.router, prefix=API_PREFIX)
app.include_router(buses.router, prefix=API_PREFIX)
app.include_router(routes.router, prefix=API_PREFIX)
app.include_router(attendance.router, prefix=API_PREFIX)
app.include_router(requests.router, prefix=API_PREFIX)
app.include_router(tracking.router, prefix=API_PREFIX)
app.include_router(requests.router, prefix=f"{API_PREFIX}/transport-requests", tags=["Transport Requests Alias"])


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------
@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok", "service": "NeoYatra API", "environment": os.getenv("ENVIRONMENT", "production")}
