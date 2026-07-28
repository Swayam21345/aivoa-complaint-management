from typing import Any

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config import get_settings

settings = get_settings()

# ─── Async engine ─────────────────────────────────────────────────────────────
engine_kwargs: dict[str, Any] = {"echo": settings.debug}
if "sqlite" in settings.database_url:
    from sqlalchemy.pool import StaticPool
    engine_kwargs.update({
        "connect_args": {"check_same_thread": False},
        "poolclass": StaticPool,
    })
else:
    engine_kwargs.update({
        "pool_pre_ping": True,
        "pool_size": 10,
        "max_overflow": 20,
    })

engine = create_async_engine(settings.database_url, **engine_kwargs)

# ─── Session factory ──────────────────────────────────────────────────────────
AsyncSessionLocal: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,       # avoid lazy-load errors after commit
    autoflush=False,
    autocommit=False,
)
