import os
import uuid
from typing import AsyncGenerator, Optional

import pytest
from fastapi import Depends
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401
import app.models.user  # noqa: F401
from app.api.dependencies import get_current_user as real_get_current_user, get_db, oauth2_scheme
from app.db.seed import seed_default_admin
from app.main import app as fastapi_app
from app.models.base import Base
from app.models.user import User

TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    async with TestingSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def override_get_current_user(
    db: AsyncSession = Depends(override_get_db),
    token: Optional[str] = Depends(oauth2_scheme),
) -> User:
    # If a Bearer token is provided in the request, decode it via real auth logic
    if token:
        return await real_get_current_user(db=db, token=token)

    # Fallback to default test admin for unauthenticated legacy test calls
    return User(
        id=uuid.UUID("11111111-1111-1111-1111-11111111111a"),
        full_name="System Administrator",
        email="admin@aiccms.local",
        password_hash="fakehash",
        role="ADMIN",
        is_active=True,
    )


@pytest.fixture(autouse=True)
async def setup_db() -> AsyncGenerator[None, None]:
    fastapi_app.dependency_overrides[get_db] = override_get_db
    fastapi_app.dependency_overrides[real_get_current_user] = override_get_current_user
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    async with TestingSessionLocal() as session:
        await seed_default_admin(session)
    yield
    fastapi_app.dependency_overrides.pop(get_db, None)
    fastapi_app.dependency_overrides.pop(real_get_current_user, None)


@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(
        transport=ASGITransport(app=fastapi_app), base_url="http://test"
    ) as client:
        yield client


async def _authenticated_role_client(
    async_client: AsyncClient,
    email: str,
    password: str,
) -> AsyncClient:
    login_res = await async_client.post(
        "/api/auth/login",
        json={"email": email, "password": password},
    )
    token = login_res.json().get("access_token", "") if login_res.status_code == 200 else ""
    return AsyncClient(
        transport=ASGITransport(app=fastapi_app),
        base_url="http://test",
        headers={"Authorization": f"Bearer {token}"},
    )


@pytest.fixture
async def admin_client(async_client: AsyncClient) -> AsyncGenerator[AsyncClient, None]:
    client = await _authenticated_role_client(async_client, "admin@aiccms.local", "Admin@123")
    async with client:
        yield client


@pytest.fixture
async def qa_manager_client(async_client: AsyncClient) -> AsyncGenerator[AsyncClient, None]:
    client = await _authenticated_role_client(async_client, "qa@aiccms.local", "QAManager@123")
    async with client:
        yield client


@pytest.fixture
async def investigator_client(async_client: AsyncClient) -> AsyncGenerator[AsyncClient, None]:
    client = await _authenticated_role_client(async_client, "investigator@aiccms.local", "Investigator@123")
    async with client:
        yield client


@pytest.fixture
async def viewer_client(async_client: AsyncClient) -> AsyncGenerator[AsyncClient, None]:
    client = await _authenticated_role_client(async_client, "viewer@aiccms.local", "Viewer@123")
    async with client:
        yield client
