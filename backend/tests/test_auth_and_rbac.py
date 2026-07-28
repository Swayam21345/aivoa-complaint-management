from datetime import timedelta
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete

from app.api.dependencies import get_current_user
from app.core.security import create_access_token, hash_password
from app.main import app as fastapi_app
from app.models.user import User


from tests.conftest import TestingSessionLocal
from app.models.base import Base


@pytest.fixture
async def seed_users(async_client: AsyncClient) -> dict[str, User]:
    """
    Seed test users with different roles into the test database.
    """
    # Pop get_current_user override so real authentication is tested
    fastapi_app.dependency_overrides.pop(get_current_user, None)

    async with TestingSessionLocal() as session:
        await session.execute(delete(User))
        await session.commit()

        admin = User(
            full_name="Admin User",
            email="admin@test.local",
            password_hash=hash_password("AdminPass123"),
            role="ADMIN",
            is_active=True,
        )
        qa = User(
            full_name="QA Manager User",
            email="qa@test.local",
            password_hash=hash_password("QAPass123"),
            role="QA_MANAGER",
            is_active=True,
        )
        investigator = User(
            full_name="Investigator User",
            email="investigator@test.local",
            password_hash=hash_password("InvestigatorPass123"),
            role="INVESTIGATOR",
            is_active=True,
        )
        viewer = User(
            full_name="Viewer User",
            email="viewer@test.local",
            password_hash=hash_password("ViewerPass123"),
            role="VIEWER",
            is_active=True,
        )
        session.add_all([admin, qa, investigator, viewer])
        await session.commit()
        await session.refresh(admin)
        await session.refresh(qa)
        await session.refresh(investigator)
        await session.refresh(viewer)
        return {
            "ADMIN": admin,
            "QA_MANAGER": qa,
            "INVESTIGATOR": investigator,
            "VIEWER": viewer,
        }


@pytest.mark.asyncio
async def test_login_success(async_client: AsyncClient, seed_users: dict[str, User]) -> None:
    login_payload = {
        "email": "admin@test.local",
        "password": "AdminPass123",
    }
    response = await async_client.post("/api/auth/login", json=login_payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["expires_in"] == 3600


@pytest.mark.asyncio
async def test_login_failure_invalid_password(async_client: AsyncClient, seed_users: dict[str, User]) -> None:
    login_payload = {
        "email": "admin@test.local",
        "password": "WrongPassword",
    }
    response = await async_client.post("/api/auth/login", json=login_payload)
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"


@pytest.mark.asyncio
async def test_login_failure_non_existent_email(async_client: AsyncClient, seed_users: dict[str, User]) -> None:
    login_payload = {
        "email": "unknown@test.local",
        "password": "AdminPass123",
    }
    response = await async_client.post("/api/auth/login", json=login_payload)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_me_success(async_client: AsyncClient, seed_users: dict[str, User]) -> None:
    user = seed_users["QA_MANAGER"]
    token = create_access_token(subject=user.id, role=user.role)
    headers = {"Authorization": f"Bearer {token}"}

    response = await async_client.get("/api/auth/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "qa@test.local"
    assert data["name"] == "QA Manager User"
    assert data["role"] == "QA_MANAGER"


@pytest.mark.asyncio
async def test_get_me_unauthorized_missing_token(async_client: AsyncClient, seed_users: dict[str, User]) -> None:
    response = await async_client.get("/api/auth/me")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_expired_jwt_token(async_client: AsyncClient, seed_users: dict[str, User]) -> None:
    user = seed_users["VIEWER"]
    expired_token = create_access_token(
        subject=user.id,
        role=user.role,
        expires_delta=timedelta(seconds=-10),
    )
    headers = {"Authorization": f"Bearer {expired_token}"}
    response = await async_client.get("/api/auth/me", headers=headers)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_role_based_authorization(async_client: AsyncClient, seed_users: dict[str, User]) -> None:
    viewer_token = create_access_token(subject=seed_users["VIEWER"].id, role="VIEWER")
    qa_token = create_access_token(subject=seed_users["QA_MANAGER"].id, role="QA_MANAGER")

    complaint_payload = {
        "product_name": "Aspirin 100mg",
        "batch_number": "BATCH-2026-A1",
        "customer_name": "City Clinic",
        "category": "Packaging Defect",
        "risk_level": "Low",
        "priority": "Low",
        "complaint_text": "Torn outer box.",
    }

    # 1. Viewer trying to create a complaint -> 403 Forbidden
    res_viewer = await async_client.post(
        "/api/complaints",
        json=complaint_payload,
        headers={"Authorization": f"Bearer {viewer_token}"},
    )
    assert res_viewer.status_code == 403

    # 2. QA Manager trying to create a complaint -> 201 Created
    res_qa = await async_client.post(
        "/api/complaints",
        json=complaint_payload,
        headers={"Authorization": f"Bearer {qa_token}"},
    )
    assert res_qa.status_code == 201
