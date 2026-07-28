from pydantic import BaseModel, Field


class DashboardKPIResponse(BaseModel):
    total_complaints: int = Field(..., description="Total active complaints count")
    new_count: int = Field(..., description="Complaints with status NEW")
    under_review_count: int = Field(..., description="Complaints with status UNDER_REVIEW")
    in_progress_count: int = Field(..., description="Complaints with status IN_PROGRESS")
    resolved_count: int = Field(..., description="Complaints with status RESOLVED")
    closed_count: int = Field(..., description="Complaints with status CLOSED")
    critical_priority_count: int = Field(..., description="Complaints with Critical priority")
    high_risk_count: int = Field(..., description="Complaints with High risk level")
    created_today_count: int = Field(..., description="Complaints received or created today")
    created_this_month_count: int = Field(..., description="Complaints created in the current month")


class DistributionItem(BaseModel):
    label: str
    count: int


class MonthlyTrendItem(BaseModel):
    month: str  # e.g., "2026-07"
    count: int


class DashboardTrendsResponse(BaseModel):
    by_status: list[DistributionItem]
    by_category: list[DistributionItem]
    by_risk_level: list[DistributionItem]
    by_priority: list[DistributionItem]
    monthly_trend: list[MonthlyTrendItem]
