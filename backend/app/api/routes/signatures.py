from uuid import UUID

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user, get_db, require_roles
from app.models.user import User
from app.schemas.electronic_signature import (
    ElectronicSignatureCreate,
    ElectronicSignatureRead,
    ElectronicSignatureResponse,
)
from app.services.signature_service import create_signature, get_signature_history

router = APIRouter(prefix="/complaints", tags=["Electronic Signatures (21 CFR Part 11)"])


@router.post(
    "/{complaint_id}/sign",
    response_model=ElectronicSignatureResponse,
    status_code=200,
    summary="21 CFR Part 11 Electronic Signature",
    description=(
        "Executes a legally binding 21 CFR Part 11 electronic signature for "
        "critical QMS workflow actions. Re-authenticates the current user's password, "
        "generates a SHA-256 cryptographic checksum, and creates an immutable audit record."
    ),
    dependencies=[Depends(require_roles("ADMIN", "QA_MANAGER"))],
)
async def sign_complaint_endpoint(
    complaint_id: UUID,
    payload: ElectronicSignatureCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ElectronicSignatureResponse:
    ip_address: str | None = request.client.host if request.client else None
    user_agent: str | None = request.headers.get("User-Agent")

    return await create_signature(
        db=db,
        complaint_id=complaint_id,
        payload=payload,
        current_user=current_user,
        ip_address=ip_address,
        user_agent=user_agent,
    )


@router.get(
    "/{complaint_id}/signatures",
    response_model=list[ElectronicSignatureRead],
    summary="List complaint electronic signatures",
    description=(
        "Retrieve all immutable 21 CFR Part 11 electronic signature records "
        "for a specific complaint, ordered newest-first."
    ),
)
async def get_complaint_signatures_endpoint(
    complaint_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ElectronicSignatureRead]:
    return await get_signature_history(db=db, complaint_id=complaint_id)
