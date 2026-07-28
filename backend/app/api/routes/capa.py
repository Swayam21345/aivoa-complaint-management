from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user, get_db, require_roles
from app.models.user import User
from app.schemas.capa import (
    CAPACloseRequest,
    CAPACreate,
    CAPADashboardRead,
    CAPAEffectivenessReview,
    CAPAListResponse,
    CAPARead,
    CAPAUpdate,
)
from app.services.capa_service import CAPAService

router = APIRouter(prefix="/capa", tags=["CAPA Management"])


@router.get(
    "",
    response_model=CAPAListResponse,
    dependencies=[Depends(require_roles("ADMIN", "QA_MANAGER", "INVESTIGATOR", "VIEWER"))],
    summary="List CAPA records with filtering, search, and pagination",
)
async def list_capas(
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    risk_level: Optional[str] = Query(None),
    complaint_id: Optional[UUID] = Query(None),
    owner: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc"),
) -> CAPAListResponse:
    """
    Retrieve paginated CAPA records with optional search and filters.
    """
    return await CAPAService.list_capas(
        db=db,
        page=page,
        page_size=page_size,
        status=status,
        priority=priority,
        risk_level=risk_level,
        complaint_id=complaint_id,
        owner=owner,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
    )


@router.post(
    "",
    response_model=CAPARead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles("ADMIN", "QA_MANAGER", "INVESTIGATOR"))],
    summary="Create a new CAPA record",
)
async def create_capa(
    payload: CAPACreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CAPARead:
    """
    Create a new Corrective and Preventive Action (CAPA) record linked to a complaint.
    """
    return await CAPAService.create_capa(db=db, payload=payload, current_user=current_user)


@router.get(
    "/dashboard",
    response_model=CAPADashboardRead,
    dependencies=[Depends(require_roles("ADMIN", "QA_MANAGER", "INVESTIGATOR", "VIEWER"))],
    summary="Get CAPA dashboard analytics & KPI metrics",
)
async def get_capa_dashboard(
    db: AsyncSession = Depends(get_db),
) -> CAPADashboardRead:
    """
    Calculate and return CAPA KPI metrics, status distributions, and monthly trends.
    """
    return await CAPAService.get_dashboard_metrics(db=db)


@router.get(
    "/{id}",
    response_model=CAPARead,
    dependencies=[Depends(require_roles("ADMIN", "QA_MANAGER", "INVESTIGATOR", "VIEWER"))],
    summary="Get CAPA detail by UUID",
)
async def get_capa_by_id(
    id: UUID,
    db: AsyncSession = Depends(get_db),
) -> CAPARead:
    """
    Retrieve full details for a specific CAPA record.
    """
    return await CAPAService.get_capa_detail(db=db, capa_id=id)


@router.patch(
    "/{id}",
    response_model=CAPARead,
    dependencies=[Depends(require_roles("ADMIN", "QA_MANAGER", "INVESTIGATOR"))],
    summary="Update CAPA record details or implementation status",
)
async def update_capa(
    id: UUID,
    payload: CAPAUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CAPARead:
    """
    Update fields or workflow status on a CAPA record.
    """
    return await CAPAService.update_capa(db=db, capa_id=id, payload=payload, current_user=current_user)


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_roles("ADMIN"))],
    summary="Delete a CAPA record (Admin only)",
)
async def delete_capa(
    id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """
    Delete a CAPA record. Requires ADMIN permissions.
    """
    await CAPAService.delete_capa(db=db, capa_id=id, current_user=current_user)


@router.post(
    "/{id}/effectiveness",
    response_model=CAPARead,
    dependencies=[Depends(require_roles("ADMIN", "QA_MANAGER"))],
    summary="Submit 21 CFR Part 11 signed CAPA effectiveness review",
)
async def review_capa_effectiveness(
    id: UUID,
    payload: CAPAEffectivenessReview,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CAPARead:
    """
    Conduct an effectiveness check review with 21 CFR Part 11 password re-authentication.
    Transitions status to EFFECTIVE or INEFFECTIVE.
    """
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    return await CAPAService.review_effectiveness(
        db=db,
        capa_id=id,
        review_data=payload,
        current_user=current_user,
        ip_address=ip_address,
        user_agent=user_agent,
    )


@router.post(
    "/{id}/close",
    response_model=CAPARead,
    dependencies=[Depends(require_roles("ADMIN", "QA_MANAGER"))],
    summary="Close CAPA with 21 CFR Part 11 electronic signature",
)
async def close_capa(
    id: UUID,
    payload: CAPACloseRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CAPARead:
    """
    Close a CAPA record with 21 CFR Part 11 password re-authentication signature.
    """
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    return await CAPAService.close_capa(
        db=db,
        capa_id=id,
        close_data=payload,
        current_user=current_user,
        ip_address=ip_address,
        user_agent=user_agent,
    )
