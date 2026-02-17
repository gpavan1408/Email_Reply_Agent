"""
database.py — Database connection setup using SQLAlchemy.

What this does:
  Creates the connection to MySQL.
  Sets up async sessions so FastAPI can handle many requests
  at the same time without blocking.

Key concepts:
  engine       = the actual connection to MySQL
  session      = a single conversation with the database
  Base         = parent class for all our database models (Phase 2)
  get_db()     = FastAPI dependency — gives each request its own session
"""

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
)
from sqlalchemy.orm import DeclarativeBase
from loguru import logger
from app.utils.config import settings


# ── Engine 
# The engine is the connection pool to MySQL.
# pool_pre_ping=True means it reconnects if the connection drops.
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.APP_ENV == "development",  # Prints SQL in dev
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
)

# ── Session Factory 
# Creates new sessions when needed.
# expire_on_commit=False means objects stay accessible after commit.
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# ── Base Model 
# All SQLAlchemy models (Phase 2) will inherit from this.
class Base(DeclarativeBase):
    pass


# ── FastAPI Dependency ─
async def get_db():
    """
    Yields a database session for each incoming API request.
    Automatically commits on success, rolls back on error.

    Usage in FastAPI routes (Phase 5):
      from app.db.database import get_db
      async def my_route(db: AsyncSession = Depends(get_db)):
          ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# ── Startup Check ──
async def init_db():
    """
    Called at app startup to verify DB connection works.
    Tables are created by Alembic migrations (Phase 2).
    """
    try:
        async with engine.begin() as conn:
            logger.info("✅ MySQL connection established")
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        raise