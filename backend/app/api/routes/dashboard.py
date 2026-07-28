from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any, Dict

from app.api.dependencies import get_current_user, get_db, require_roles
from app.models.user import User
from app.schemas.complaint import InvestigatorDashboardRead
from app.schemas.dashboard import DashboardKPIResponse, DashboardTrendsResponse
from app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get(
    "",
    response_model=DashboardKPIResponse,
    dependencies=[Depends(require_roles("ADMIN", "QA_MANAGER", "INVESTIGATOR", "VIEWER"))],
)
async def get_dashboard_kpis(
    db: AsyncSession = Depends(get_db),
) -> DashboardKPIResponse:
    """
    Get aggregated high-level KPI metrics for complaints dashboard.
    """
    return await DashboardService.get_kpis(db)


@router.get(
    "/metrics",
    response_model=None,
    dependencies=[Depends(require_roles("ADMIN", "QA_MANAGER", "INVESTIGATOR", "VIEWER"))],
)
async def get_dashboard_metrics(
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    Get combined KPIs + 21 CFR Part 11 electronic signature metrics.
    Includes unsigned_qa_reviews, unsigned_closures, recent_signatures_count.
    """
    return await DashboardService.get_dashboard_metrics(db)


@router.get(
    "/investigator",
    response_model=InvestigatorDashboardRead,
    dependencies=[Depends(require_roles("ADMIN", "QA_MANAGER", "INVESTIGATOR"))],
)
async def get_investigator_kpis(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> InvestigatorDashboardRead:
    """
    Get personalized Investigator KPI dashboard (Assigned To Me, Pending Reviews, Overdue Cases, Completed This Month).
    """
    return await DashboardService.get_investigator_kpis(db, current_user.full_name)


@router.get(
    "/trends",
    response_model=DashboardTrendsResponse,
    dependencies=[Depends(require_roles("ADMIN", "QA_MANAGER", "INVESTIGATOR", "VIEWER"))],
)
async def get_dashboard_trends(
    db: AsyncSession = Depends(get_db),
) -> DashboardTrendsResponse:
    """
    Get complaint analytics distributions and trends (by status, category, risk level, priority, monthly).
    """
    return await DashboardService.get_trends(db)

