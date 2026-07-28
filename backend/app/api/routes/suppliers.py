from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user, get_db, require_roles
from app.models.supplier import Supplier
from app.models.user import User
from app.schemas.supplier import (
    SupplierApprovalCreate,
    SupplierAuditCreate,
    SupplierAuditRead,
    SupplierCorrectiveActionCreate,
    SupplierCorrectiveActionRead,
    SupplierCreate,
    SupplierDashboardRead,
    SupplierNonconformanceCreate,
    SupplierNonconformanceRead,
    SupplierRead,
    SupplierReportRead,
    SupplierScorecardCreate,
    SupplierScorecardRead,
    SupplierUpdate,
)
from app.services import supplier_service

router = APIRouter(prefix="/suppliers", tags=["Supplier Quality Management"])


@router.get("", response_model=Dict[str, Any])
async def list_suppliers(
    status_filter: Optional[str] = Query(None, alias="status"),
    risk_level: Optional[str] = Query(None),
    supplier_type: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    suppliers, total = await supplier_service.list_suppliers(
        db, status_filter, risk_level, supplier_type, search, page, page_size
    )
    return {
        "items": [SupplierRead.model_validate(s) for s in suppliers],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.post("", response_model=SupplierRead, status_code=status.HTTP_201_CREATED)
async def create_supplier(
    payload: SupplierCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN", "QA_MANAGER", "PURCHASING")),
) -> SupplierRead:
    supplier = await supplier_service.create_supplier(db, payload, current_user)
    return SupplierRead.model_validate(supplier)


@router.get("/dashboard", response_model=SupplierDashboardRead)
async def get_supplier_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SupplierDashboardRead:
    metrics = await supplier_service.get_supplier_dashboard_metrics(db)
    return SupplierDashboardRead(**metrics)


@router.get("/report", response_model=SupplierReportRead)
async def get_supplier_report(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN", "QA_MANAGER", "PURCHASING")),
) -> SupplierReportRead:
    suppliers, total = await supplier_service.list_suppliers(db, page_size=1000)
    approved_count = len([s for s in suppliers if s.status == "APPROVED"])
    high_risk_count = len([s for s in suppliers if s.risk_level in ("HIGH", "CRITICAL")])
    ncr_count = sum(len(s.nonconformances) for s in suppliers)

    return SupplierReportRead(
        total_suppliers=total,
        approved_count=approved_count,
        high_risk_count=high_risk_count,
        open_ncr_count=ncr_count,
        suppliers=[SupplierRead.model_validate(s) for s in suppliers],
    )


@router.get("/{id}", response_model=SupplierRead)
async def get_supplier_detail(
    id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SupplierRead:
    supplier = await supplier_service.get_supplier_detail(db, id)
    return SupplierRead.model_validate(supplier)


@router.patch("/{id}", response_model=SupplierRead)
async def update_supplier(
    id: UUID,
    payload: SupplierUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN", "QA_MANAGER", "PURCHASING")),
) -> SupplierRead:
    supplier = await supplier_service.update_supplier(db, id, payload, current_user)
    return SupplierRead.model_validate(supplier)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_supplier(
    id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN", "QA_MANAGER")),
) -> None:
    await supplier_service.delete_supplier(db, id, current_user)


@router.post("/{id}/approve", response_model=SupplierRead)
async def approve_supplier(
    id: UUID,
    payload: SupplierApprovalCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN", "QA_MANAGER")),
) -> SupplierRead:
    supplier = await supplier_service.approve_supplier(db, id, payload, current_user)
    return SupplierRead.model_validate(supplier)


@router.post("/{id}/audit", response_model=SupplierAuditRead)
async def schedule_supplier_audit(
    id: UUID,
    payload: SupplierAuditCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN", "QA_MANAGER", "PURCHASING")),
) -> SupplierAuditRead:
    audit = await supplier_service.schedule_supplier_audit(db, id, payload, current_user)
    return SupplierAuditRead.model_validate(audit)


@router.post("/{id}/scorecard", response_model=SupplierScorecardRead)
async def add_supplier_scorecard(
    id: UUID,
    payload: SupplierScorecardCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN", "QA_MANAGER", "PURCHASING")),
) -> SupplierScorecardRead:
    scorecard = await supplier_service.add_supplier_scorecard(db, id, payload, current_user)
    return SupplierScorecardRead.model_validate(scorecard)


@router.post("/{id}/nonconformance", response_model=SupplierNonconformanceRead)
async def add_supplier_nonconformance(
    id: UUID,
    payload: SupplierNonconformanceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN", "QA_MANAGER", "PURCHASING")),
) -> SupplierNonconformanceRead:
    ncr = await supplier_service.add_supplier_nonconformance(db, id, payload, current_user)
    return SupplierNonconformanceRead.model_validate(ncr)


@router.post("/{id}/corrective-action", response_model=SupplierCorrectiveActionRead)
async def add_supplier_corrective_action(
    id: UUID,
    payload: SupplierCorrectiveActionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN", "QA_MANAGER", "PURCHASING")),
) -> SupplierCorrectiveActionRead:
    sca = await supplier_service.add_supplier_corrective_action(db, id, payload, current_user)
    return SupplierCorrectiveActionRead.model_validate(sca)

