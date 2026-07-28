from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user, get_db
from app.config import get_settings
from app.core.security import create_access_token, verify_password
from app.models.user import User
from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.user import UserResponse
from app.services.workflow_service import log_audit_event

settings = get_settings()

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="User login",
    description="Authenticate user with email and password (supports both JSON payload and OAuth2 Form Data), returning JWT access token.",
)
async def login(
    request: Request,
    payload: LoginRequest | None = None,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    content_type = request.headers.get("content-type", "")

    if "application/x-www-form-urlencoded" in content_type or "multipart/form-data" in content_type:
        form = await request.form()
        email = str(form.get("username", "") or form.get("email", ""))
        password = str(form.get("password", ""))
    elif payload is not None:
        email = payload.email
        password = payload.password
    else:
        try:
            body = await request.json()
            email = str(body.get("email", "") or body.get("username", ""))
            password = str(body.get("password", ""))
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid request body format",
            )

    # Query user by email
    stmt = select(User).where(User.email == email)
    result = await db.execute(stmt)
    user: User | None = result.scalar_one_or_none()

    if user is None or not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is deactivated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(subject=user.id, role=user.role)
    expires_in_seconds = settings.access_token_expire_minutes * 60

    # Log Login Audit Event
    await log_audit_event(
        db,
        action_type="Login",
        description=f"User '{user.email}' ({user.role}) logged in successfully.",
        actor_email=user.email,
    )
    await db.flush()

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": expires_in_seconds,
    }


@router.post(
    "/logout",
    summary="User logout",
    description="Logs an audit event for user sign-out.",
)
async def logout(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, str]:
    await log_audit_event(
        db,
        action_type="Logout",
        description=f"User '{current_user.email}' logged out.",
        actor_email=current_user.email,
    )
    await db.flush()
    return {"detail": "Logged out successfully"}


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user info",
    description="Return user profile details for the currently authenticated user.",
)
async def get_me(
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    return UserResponse.from_user(current_user)
