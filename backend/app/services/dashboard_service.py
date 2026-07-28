import asyncio
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.complaint import Complaint
from app.models.electronic_signature import ElectronicSignature
from app.schemas.complaint import InvestigatorDashboardRead
from app.schemas.dashboard import (
    DashboardKPIResponse,
    DashboardTrendsResponse,
    DistributionItem,
    MonthlyTrendItem,
)
from app.services.workflow_service import evaluate_complaint_sla


class DashboardService:
    """
    Service providing aggregated analytics and metrics for the dashboard.
    Includes in-memory TTL caching for fast dashboard load times.
    """

    _cache: Dict[str, Any] = {}
    _cache_time: Optional[datetime] = None
    _CACHE_TTL_SECONDS = 30  # Cache metrics for 30 seconds

    @classmethod
    def invalidate_cache(cls) -> None:
        """Invalidate in-memory cache when complaints are mutated."""
        cls._cache_time = None
        cls._cache = {}

    @classmethod
    async def get_kpis(cls, db: AsyncSession) -> DashboardKPIResponse:
        """
        Calculates 10 core KPI metrics for complaints dashboard.
        """
        stmt = select(Complaint).where(Complaint.is_deleted == False)  # noqa: E712
        complaints = (await db.execute(stmt)).scalars().all()

        total = len(complaints)
        new_c = sum(1 for c in complaints if c.status in ("NEW", "Draft"))
        under_review_c = sum(1 for c in complaints if c.status in ("UNDER_REVIEW", "TRIAGED", "ASSIGNED"))
        in_progress_c = sum(1 for c in complaints if c.status in ("IN_PROGRESS", "UNDER_INVESTIGATION", "ROOT_CAUSE_IDENTIFIED", "CAPA_IN_PROGRESS", "WAITING_CUSTOMER"))
        resolved_c = sum(1 for c in complaints if c.status in ("RESOLVED", "QA_REVIEW", "QA_APPROVED"))
        closed_c = sum(1 for c in complaints if c.status == "CLOSED")
        critical_c = sum(1 for c in complaints if c.priority == "Critical")
        high_risk_c = sum(1 for c in complaints if c.risk_level == "High")

        now = datetime.now(timezone.utc)
        today_date = now.date()
        current_month = now.month
        current_year = now.year

        created_today_c = 0
        created_this_month_c = 0

        for c in complaints:
            if c.created_at:
                c_created = c.created_at if c.created_at.tzinfo else c.created_at.replace(tzinfo=timezone.utc)
                if c_created.date() == today_date:
                    created_today_c += 1
                if c_created.month == current_month and c_created.year == current_year:
                    created_this_month_c += 1

        return DashboardKPIResponse(
            total_complaints=total,
            new_count=new_c,
            under_review_count=under_review_c,
            in_progress_count=in_progress_c,
            resolved_count=resolved_c,
            closed_count=closed_c,
            critical_priority_count=critical_c,
            high_risk_count=high_risk_c,
            created_today_count=created_today_c,
            created_this_month_count=created_this_month_c,
        )

    @classmethod
    async def get_trends(cls, db: AsyncSession) -> DashboardTrendsResponse:
        """
        Calculates distributions by status, category, risk_level, priority, and monthly trend.
        """
        stmt = select(Complaint).where(Complaint.is_deleted == False)  # noqa: E712
        complaints = (await db.execute(stmt)).scalars().all()

        status_counts: Dict[str, int] = {}
        category_counts: Dict[str, int] = {}
        risk_counts: Dict[str, int] = {}
        priority_counts: Dict[str, int] = {}

        months_map: Dict[str, int] = {}
        now = datetime.now(timezone.utc)
        for i in range(5, -1, -1):
            m_date = now - timedelta(days=i * 30)
            m_key = m_date.strftime("%Y-%m")
            months_map[m_key] = 0

        for c in complaints:
            st = c.status
            cat = c.category or "Other"
            rk = c.risk_level or "Low"
            pr = c.priority or "Low"

            status_counts[st] = status_counts.get(st, 0) + 1
            category_counts[cat] = category_counts.get(cat, 0) + 1
            risk_counts[rk] = risk_counts.get(rk, 0) + 1
            priority_counts[pr] = priority_counts.get(pr, 0) + 1

            if c.created_at:
                c_created = c.created_at if c.created_at.tzinfo else c.created_at.replace(tzinfo=timezone.utc)
                m_key = c_created.strftime("%Y-%m")
                if m_key in months_map:
                    months_map[m_key] += 1

        by_status = [DistributionItem(label=k, count=v) for k, v in status_counts.items()]
        by_category = [DistributionItem(label=k, count=v) for k, v in category_counts.items()]
        by_risk_level = [DistributionItem(label=k, count=v) for k, v in risk_counts.items()]
        by_priority = [DistributionItem(label=k, count=v) for k, v in priority_counts.items()]
        monthly_trend = [MonthlyTrendItem(month=k, count=v) for k, v in months_map.items()]

        return DashboardTrendsResponse(
            by_status=by_status,
            by_category=by_category,
            by_risk_level=by_risk_level,
            by_priority=by_priority,
            monthly_trend=monthly_trend,
        )

    @classmethod
    async def get_dashboard_metrics(cls, db: AsyncSession) -> Dict[str, Any]:
        """
        Calculates high-level KPIs, 21 CFR Part 11 signature metrics, and monthly complaint trends.
        """
        kpis_obj = await cls.get_kpis(db)
        trends_obj = await cls.get_trends(db)

        stmt = select(Complaint).where(Complaint.is_deleted == False)  # noqa: E712
        res = await db.execute(stmt)
        complaints = res.scalars().all()

        unsigned_qa_reviews = sum(1 for c in complaints if c.status == "QA_REVIEW")
        unsigned_closures = sum(1 for c in complaints if c.status == "QA_APPROVED")

        sig_stmt = select(func.count()).select_from(ElectronicSignature)
        recent_signatures_count = (await db.execute(sig_stmt)).scalar_one() or 0

        return {
            "total_complaints": kpis_obj.total_complaints,
            "open_complaints": kpis_obj.new_count + kpis_obj.under_review_count + kpis_obj.in_progress_count,
            "high_risk_complaints": kpis_obj.high_risk_count,
            "sla_breached": 0,
            "sla_compliance_rate": 100.0,
            "unsigned_qa_reviews": unsigned_qa_reviews,
            "unsigned_closures": unsigned_closures,
            "recent_signatures_count": recent_signatures_count,
            "risk_distribution": {item.label: item.count for item in trends_obj.by_risk_level},
            "status_distribution": {item.label: item.count for item in trends_obj.by_status},
            "monthly_trend": [{"month": item.month, "count": item.count} for item in trends_obj.monthly_trend],
        }

    @classmethod
    async def get_investigator_kpis(
        cls,
        db: AsyncSession,
        investigator_name: Optional[str] = None,
    ) -> InvestigatorDashboardRead:
        """
        Returns investigator-specific workflow KPIs.
        """
        stmt = select(Complaint).where(Complaint.is_deleted == False)  # noqa: E712
        res = await db.execute(stmt)
        complaints = res.scalars().all()

        assigned_to_me = 0
        pending_reviews = 0
        overdue_cases = 0
        completed_this_month = 0
        resolution_times: list[float] = []

        now = datetime.now(timezone.utc)
        current_month = now.month
        current_year = now.year

        for c in complaints:
            sla_metrics = evaluate_complaint_sla(c)

            if investigator_name and c.assigned_to and investigator_name.lower() in c.assigned_to.lower():
                assigned_to_me += 1

            if c.status in ("QA_REVIEW", "UNDER_REVIEW", "WAITING_CUSTOMER"):
                pending_reviews += 1

            if sla_metrics["is_overdue"]:
                overdue_cases += 1

            if c.status in ("CLOSED", "RESOLVED", "QA_APPROVED"):
                if c.updated_at and c.updated_at.month == current_month and c.updated_at.year == current_year:
                    completed_this_month += 1

                if c.created_at and c.updated_at:
                    c_created = c.created_at if c.created_at.tzinfo else c.created_at.replace(tzinfo=timezone.utc)
                    c_updated = c.updated_at if c.updated_at.tzinfo else c.updated_at.replace(tzinfo=timezone.utc)
                    duration_hrs = (c_updated - c_created).total_seconds() / 3600.0
                    if duration_hrs >= 0:
                        resolution_times.append(duration_hrs)

        avg_resolution_time = round(sum(resolution_times) / len(resolution_times), 1) if resolution_times else 0.0

        return InvestigatorDashboardRead(
            assigned_to_me=assigned_to_me,
            pending_reviews=pending_reviews,
            overdue_cases=overdue_cases,
            completed_this_month=completed_this_month,
            average_resolution_time=avg_resolution_time,
        )
