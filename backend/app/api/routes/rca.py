from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user, get_db, require_roles
from app.models.user import User
from app.schemas.rca import (
    FMEAAssessmentCreate,
    FMEAAssessmentRead,
    RCAApproveRequest,
    RCACreate,
    RCADashboardRead,
    RCAListResponse,
    RCARead,
    RCAUpdate,
)
from app.services.rca_service import RCAService

router = APIRouter(prefix="/rca", tags=["Root Cause Analysis & Risk Management"])


@router.get(
    "",
    response_model=RCAListResponse,
    dependencies=[Depends(require_roles("ADMIN", "QA_MANAGER", "INVESTIGATOR", "VIEWER"))],
    summary="List RCA investigation records with pagination and filters",
)
async def list_rcas(
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    status: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    complaint_id: Optional[UUID] = Query(None),
    search: Optional[str] = Query(None),
) -> RCAListResponse:
    return await RCAService.list_rcas(
        db=db,
        page=page,
        page_size=page_size,
        status=status,
        category=category,
        complaint_id=complaint_id,
        search=search,
    )


@router.post(
    "",
    response_model=RCARead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles("ADMIN", "QA_MANAGER", "INVESTIGATOR"))],
    summary="Create a new Root Cause Analysis & FMEA record",
)
async def create_rca(
    payload: RCACreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> RCARead:
    return await RCAService.create_rca(db=db, payload=payload, current_user=current_user)


@router.get(
    "/dashboard",
    response_model=RCADashboardRead,
    dependencies=[Depends(require_roles("ADMIN", "QA_MANAGER", "INVESTIGATOR", "VIEWER"))],
    summary="Get RCA & FMEA risk dashboard analytics",
)
async def get_rca_dashboard(
    db: AsyncSession = Depends(get_db),
) -> RCADashboardRead:
    return await RCAService.get_dashboard_metrics(db=db)


@router.get(
    "/{id}",
    response_model=RCARead,
    dependencies=[Depends(require_roles("ADMIN", "QA_MANAGER", "INVESTIGATOR", "VIEWER"))],
    summary="Get RCA record by ID",
)
async def get_rca_by_id(
    id: UUID,
    db: AsyncSession = Depends(get_db),
) -> RCARead:
    return await RCAService.get_rca_detail(db=db, rca_id=id)


@router.patch(
    "/{id}",
    response_model=RCARead,
    dependencies=[Depends(require_roles("ADMIN", "QA_MANAGER", "INVESTIGATOR"))],
    summary="Update RCA findings or methodology",
)
async def update_rca(
    id: UUID,
    payload: RCAUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> RCARead:
    return await RCAService.update_rca(db=db, rca_id=id, payload=payload, current_user=current_user)


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_roles("ADMIN"))],
    summary="Delete RCA record (Admin only)",
)
async def delete_rca(
    id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    await RCAService.delete_rca(db=db, rca_id=id, current_user=current_user)


@router.post(
    "/{id}/approve",
    response_model=RCARead,
    dependencies=[Depends(require_roles("ADMIN", "QA_MANAGER"))],
    summary="Approve RCA with 21 CFR Part 11 electronic signature",
)
async def approve_rca(
    id: UUID,
    payload: RCAApproveRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> RCARead:
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    return await RCAService.approve_rca(
        db=db,
        rca_id=id,
        approve_data=payload,
        current_user=current_user,
        ip_address=ip_address,
        user_agent=user_agent,
    )


@router.post(
    "/{id}/fmea",
    response_model=FMEAAssessmentRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles("ADMIN", "QA_MANAGER", "INVESTIGATOR"))],
    summary="Add FMEA failure mode assessment item to RCA",
)
async def add_fmea_item(
    id: UUID,
    payload: FMEAAssessmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> FMEAAssessmentRead:
    return await RCAService.add_fmea_item(db=db, rca_id=id, item=payload, current_user=current_user)
