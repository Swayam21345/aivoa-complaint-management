"""
Database initialisation helper.

In production, schema changes are managed exclusively by Alembic migrations.
This module is used only for testing / local dev bootstrap.
"""
from app.db.session import engine
from app.models.base import Base

# Import all models so Base.metadata is populated before create_all runs
import app.models.complaint       # noqa: F401
import app.models.ai_analysis     # noqa: F401
import app.models.upload_record   # noqa: F401


async def init_db() -> None:
    """
    Create all tables that don't already exist.
    Does NOT drop or alter existing tables — safe to call on restart.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_db() -> None:
    """
    Drop all tables. For use in test teardown only.
    NEVER call this in production code.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
