import os
import sys
from dotenv import load_dotenv

# Ensure backend directory is in sys.path with absolute path
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

# Load environment variables
load_dotenv(dotenv_path=os.path.join(BACKEND_DIR, '.env'))
load_dotenv()  # Also load any root .env if present

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
    """Ensure database schema and default test accounts exist on boot."""
    try:
        database.initialize_database()
        print("INFO: Database schema verified and initialized.")
    except Exception as e:
        print(f"WARNING: Could not auto-initialize database on startup: {e}")


# ---------------------------------------------------------------------------
# Welcome root & Health check
# ---------------------------------------------------------------------------
@app.get("/", tags=["Root"])
def root():
    return {
        "status": "online",
        "service": "NeoYatra School Transport API",
        "documentation": "/docs",
        "health": "/health",
        "setup_test_accounts": "/api/v1/setup-test-accounts",
        "version": "1.0.0",
    }


@app.get("/health", tags=["Health"])
def health_check():
    db_status = "connected"
    counts = {}
    try:
        conn = database.connect_database()
        cur = conn.cursor()
        cur.execute("SELECT count(*) FROM admin;")
        admin_c = cur.fetchone()[0]
        cur.execute("SELECT count(*) FROM parent;")
        parent_c = cur.fetchone()[0]
        cur.execute("SELECT count(*) FROM bus;")
        bus_c = cur.fetchone()[0]
        counts = {"admins": admin_c, "parents": parent_c, "buses": bus_c}
        cur.close()
        conn.close()
    except Exception as e:
        db_status = f"error: {str(e)}"

    return {
        "status": "ok",
        "service": "NeoYatra API",
        "database": db_status,
        "records": counts,
        "environment": os.getenv("ENVIRONMENT", "production"),
    }


@app.get("/api/v1/setup-test-accounts", tags=["Setup"])
@app.post("/api/v1/setup-test-accounts", tags=["Setup"])
@app.get("/setup-test-accounts", tags=["Setup"])
@app.post("/setup-test-accounts", tags=["Setup"])
def setup_test_accounts():
    """
    Public setup helper: verifies database connection and ensures
    admin123, parent123, and driver123 test accounts exist.
    """
    try:
        database.initialize_database()
        return {
            "status": "success",
            "message": "Default test accounts have been verified and initialized in database!",
            "credentials": [
                {"role": "Admin", "username": "admin", "password": "admin123"},
                {"role": "Parent", "username": "parent", "password": "parent123", "alias": "parent1"},
                {"role": "Driver", "username": "driver", "password": "driver123", "alias": "driver1"},
            ],
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


# ---------------------------------------------------------------------------
# Routers — both under /api/v1/ and root fallback
# ---------------------------------------------------------------------------
API_PREFIX = "/api/v1"

# 1. Standard /api/v1 prefix
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

# 2. Direct root alias fallback (in case frontend calls /auth/login directly)
app.include_router(auth.router, tags=["Root Auth Alias"])
app.include_router(dashboard.router, tags=["Root Dashboard Alias"])
app.include_router(students.router, tags=["Root Students Alias"])
app.include_router(parents.router, tags=["Root Parents Alias"])
app.include_router(buses.router, tags=["Root Buses Alias"])
app.include_router(routes.router, tags=["Root Routes Alias"])
app.include_router(attendance.router, tags=["Root Attendance Alias"])
app.include_router(requests.router, tags=["Root Requests Alias"])
app.include_router(tracking.router, tags=["Root Tracking Alias"])
