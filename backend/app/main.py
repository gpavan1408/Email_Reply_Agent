"""
main.py — FastAPI Application Entry Point.

This is where the app starts.
It creates the FastAPI app, registers all routes,
connects to the database, and starts the email poller.

FastAPI automatically generates interactive API docs at:
  http://localhost:8000/docs   ← Try all endpoints here
  http://localhost:8000/redoc  ← Alternative docs view
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from loguru import logger

from app.utils.config import settings
from app.utils.logger import setup_logger
from app.db.database import init_db


# ── Lifespan ──────────────────────────────────────────────────
# Runs setup when app starts, cleanup when app stops.
@asynccontextmanager
async def lifespan(app: FastAPI):

    # ── Startup ───────────────────────────────────────────────
    setup_logger()
    logger.info("🚀 Email Reply Agent starting...")
    logger.info(f"   Environment : {settings.APP_ENV}")
    logger.info(f"   Azure OpenAI: {settings.AZURE_OPENAI_ENDPOINT}")

    await init_db()
    logger.info("✅ Database ready")

    # Scheduler starts in Phase 3
    logger.info("⏳ Email poller will start in Phase 3")

    yield  # ← App runs and handles requests here

    # ── Shutdown ──────────────────────────────────────────────
    logger.info("🛑 Email Reply Agent shutting down...")


# ── App Factory ───────────────────────────────────────────────
def create_app() -> FastAPI:
    app = FastAPI(
        title="Email Reply Agent",
        description=(
            "AI-powered email assistant. "
            "Reads emails → understands intent → drafts reply → "
            "waits for human approval → sends."
        ),
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # ── CORS ──────────────────────────────────────────────────
    # Allows React frontend (port 3000) to call this API (port 8000)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",    # React dev server
            "http://frontend:3000",     # Docker container name
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Routes ────────────────────────────────────────────────
    # Added phase by phase:
    # Phase 5: app.include_router(emails_router, prefix="/api")
    # Phase 5: app.include_router(drafts_router, prefix="/api")
    # Phase 3: app.include_router(auth_router,   prefix="/auth")

    return app


# Create the app instance
app = create_app()


# ── Health Check ──────────────────────────────────────────────
# Used by Docker and Azure Container Apps to verify app is alive
@app.get("/health", tags=["System"])
async def health_check():
    return {
        "status":      "healthy",
        "app":         "Email Reply Agent",
        "version":     "1.0.0",
        "environment": settings.APP_ENV,
    }


@app.get("/", tags=["System"])
async def root():
    return {
        "message": "📧 Email Reply Agent API is running",
        "docs":    "http://localhost:8000/docs",
        "health":  "http://localhost:8000/health",
    }