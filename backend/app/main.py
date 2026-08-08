from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db
from app.api.routes import auth, capa, complaints, dashboard, documents, internal_audits, rca, signatures, suppliers, training, upload






from app.config import get_settings
from app.db.seed import seed_default_admin
from app.db.session import AsyncSessionLocal

settings = get_settings()


# ─── Lifespan ─────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Startup / shutdown lifecycle handler.
    """
    print(f"[AICCMS] {settings.app_name} v{settings.app_version} starting up.")
    print(f"[AICCMS] Environment : {settings.environment}")
    print(f"[AICCMS] Debug mode  : {settings.debug}")
    try:
        from app.db.session import engine
        from app.models.base import Base
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("[AICCMS] Database tables verified/created successfully.")
        async with AsyncSessionLocal() as session:
            await seed_default_admin(session)
    except Exception as e:
        print(f"[AICCMS] Startup database initialization note: {e}")
    yield
    print("[AICCMS] Shutting down.")


# ─── App factory ──────────────────────────────────────────────────────────────

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description=(
            "AI-Powered Customer Complaint Management System for "
            "Pharmaceutical Manufacturing QMS. Processes complaint documents "
            "via a LangGraph AI workflow and persists structured records to PostgreSQL."
        ),
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # ── CORS ──────────────────────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_origin_regex=r"https?://.*",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Routers ───────────────────────────────────────────────────────────
    app.include_router(auth.router, prefix="/api")
    app.include_router(upload.router, prefix="/api")
    app.include_router(complaints.router, prefix="/api")
    app.include_router(capa.router, prefix="/api")
    app.include_router(rca.router, prefix="/api")
    app.include_router(documents.router, prefix="/api")
    app.include_router(dashboard.router, prefix="/api")
    app.include_router(signatures.router, prefix="/api")
    app.include_router(training.router, prefix="/api")
    app.include_router(suppliers.router, prefix="/api")
    app.include_router(internal_audits.router, prefix="/api")



    # ── Health check ──────────────────────────────────────────────────────
    @app.get(
        "/health",
        tags=["Health"],
        summary="Health check and Database status",
        response_description="Returns 200 when service and database are healthy.",
    )
    async def health_check(
        db: AsyncSession = Depends(get_db),
    ) -> JSONResponse:
        db_status = "disconnected"
        is_healthy = False
        error_detail = None

        try:
            await db.execute(text("SELECT 1"))
            db_status = "connected"
            is_healthy = True
        except Exception as e:
            error_detail = str(e)

        status_code = 200 if is_healthy else 503
        content = {
            "ok": is_healthy,
            "status": "ok" if is_healthy else "error",
            "database": db_status,
            "service": settings.app_name,
            "version": settings.app_version,
            "environment": settings.environment,
        }
        if error_detail:
            content["error"] = error_detail

        return JSONResponse(status_code=status_code, content=content)

    return app


# ─── ASGI entry point ─────────────────────────────────────────────────────────
app = create_app()
