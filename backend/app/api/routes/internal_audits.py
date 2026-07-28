from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user, get_db, require_roles
from app.models.user import User
from app.schemas.internal_audit import (
    AuditApprovalCreate,
    AuditChecklistCreate,
    AuditChecklistRead,
    AuditFindingCreate,
    AuditFindingRead,
    InspectionReadinessCreate,
    InspectionReadinessRead,
    InternalAuditCreate,
    InternalAuditDashboardRead,
    InternalAuditRead,
    InternalAuditUpdate,
)
from app.services import internal_audit_service

router = APIRouter(prefix="/internal-audits", tags=["Internal Audit Management & Inspection Readiness"])


@router.get("", response_model=Dict[str, Any])
async def list_internal_audits(
    status_filter: Optional[str] = Query(None, alias="status"),
    department: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    audits, total = await internal_audit_service.list_internal_audits(
        db, status_filter, department, search, page, page_size
    )
    return {
        "items": [InternalAuditRead.model_validate(a) for a in audits],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.post("", response_model=InternalAuditRead, status_code=status.HTTP_201_CREATED)
async def create_internal_audit(
    payload: InternalAuditCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN", "QA_MANAGER")),
) -> InternalAuditRead:
    audit = await internal_audit_service.create_internal_audit(db, payload, current_user)
    return InternalAuditRead.model_validate(audit)


@router.get("/dashboard", response_model=InternalAuditDashboardRead)
async def get_internal_audit_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> InternalAuditDashboardRead:
    metrics = await internal_audit_service.get_internal_audit_dashboard_metrics(db)
    return InternalAuditDashboardRead(**metrics)


@router.get("/readiness-packages", response_model=List[InspectionReadinessRead])
async def list_inspection_readiness_packages(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[InspectionReadinessRead]:
    packages = await internal_audit_service.list_inspection_readiness_packages(db)
    return [InspectionReadinessRead.model_validate(p) for p in packages]


@router.post("/readiness-packages", response_model=InspectionReadinessRead, status_code=status.HTTP_201_CREATED)
async def create_inspection_readiness_package(
    payload: InspectionReadinessCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN", "QA_MANAGER")),
) -> InspectionReadinessRead:
    pkg = await internal_audit_service.create_inspection_readiness_package(db, payload, current_user)
    return InspectionReadinessRead.model_validate(pkg)


@router.get("/{id}", response_model=InternalAuditRead)
async def get_internal_audit_detail(
    id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> InternalAuditRead:
    audit = await internal_audit_service.get_internal_audit_detail(db, id)
    return InternalAuditRead.model_validate(audit)


@router.patch("/{id}", response_model=InternalAuditRead)
async def update_internal_audit(
    id: UUID,
    payload: InternalAuditUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN", "QA_MANAGER")),
) -> InternalAuditRead:
    audit = await internal_audit_service.update_internal_audit(db, id, payload, current_user)
    return InternalAuditRead.model_validate(audit)


@router.post("/{id}/checklist", response_model=AuditChecklistRead)
async def add_audit_checklist_item(
    id: UUID,
    payload: AuditChecklistCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN", "QA_MANAGER", "INVESTIGATOR")),
) -> AuditChecklistRead:
    chk = await internal_audit_service.add_audit_checklist_item(db, id, payload, current_user)
    return AuditChecklistRead.model_validate(chk)


@router.post("/{id}/finding", response_model=AuditFindingRead)
async def add_audit_finding(
    id: UUID,
    payload: AuditFindingCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN", "QA_MANAGER", "INVESTIGATOR")),
) -> AuditFindingRead:
    finding = await internal_audit_service.add_audit_finding(db, id, payload, current_user)
    return AuditFindingRead.model_validate(finding)


@router.post("/{id}/approve", response_model=InternalAuditRead)
async def approve_and_close_audit(
    id: UUID,
    payload: AuditApprovalCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN", "QA_MANAGER")),
) -> InternalAuditRead:
    audit = await internal_audit_service.approve_and_close_audit(db, id, payload, current_user)
    return InternalAuditRead.model_validate(audit)

