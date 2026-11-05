import os
import sys
import logging
from dotenv import load_dotenv

# Configure basic logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

# Ensure backend directory is in sys.path with absolute path
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

# Load environment variables
load_dotenv(dotenv_path=os.path.join(BACKEND_DIR, '.env'))
load_dotenv()  # Also load any root .env if present

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import database
from routers import auth, students, parents, buses, routes, attendance, dashboard, requests, tracking

app = FastAPI(
    title="NeoYatra — School Transport Management API",
    version="1.0.0",
    description="Production FastAPI backend for NeoYatra school transport management system.",
)

# ---------------------------------------------------------------------------
# Production Configuration & CORS Hardening
# ---------------------------------------------------------------------------
ENVIRONMENT = os.getenv("ENVIRONMENT", "development").strip().lower()

# Parse allowed origins - strictly prohibit wildcard origins in production
raw_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173")
allowed_origins = [orig.strip() for orig in raw_origins.split(",") if orig.strip()]

if ENVIRONMENT == "production":
    allowed_origins = [orig for orig in allowed_origins if orig != "*"]
    if not allowed_origins:
        logging.warning("No explicit ALLOWED_ORIGINS configured in production! Falling back to secure domain.")
        allowed_origins = ["https://neoyatra.app"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept", "Origin", "X-Requested-With"],
)


@app.exception_handler(Exception)
async def global_unhandled_exception_handler(request: Request, exc: Exception):
    """
    Catch-all exception handler to prevent leaking internal database schemas,
    stack traces, or credential fragments in HTTP responses.
    """
    logging.exception(f"Unhandled exception during request {request.method} {request.url.path}: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred. Please contact system support."},
    )


@app.on_event("startup")
def on_startup():
    """Ensure database schema, validate production secrets on boot."""
    if ENVIRONMENT == "production":
        import security
        try:
            security.get_jwt_secret()
            logging.info("Production security configuration validated: JWT_SECRET verified.")
        except RuntimeError as e:
            logging.critical(f"FATAL: Application failed to boot due to insecure production configuration: {e}")
            raise e

    try:
        database.initialize_database()
        logging.info("Database schema verified and initialized.")
    except Exception as e:
        logging.warning(f"Could not auto-initialize database on startup: {e}")


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
        logging.error(f"Health check database ping failed: {e}")
        db_status = "unhealthy"

    return {
        "status": "ok",
        "service": "NeoYatra API",
        "database": db_status,
        "records": counts,
        "environment": ENVIRONMENT,
    }


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
