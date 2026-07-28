from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CAPACreate(BaseModel):
    complaint_id: UUID = Field(..., description="UUID of the parent complaint record")
    title: str = Field(..., min_length=3, max_length=255, description="CAPA title")
    description: str = Field(..., min_length=5, description="Detailed CAPA problem description")
    root_cause: Optional[str] = Field(None, description="Identified root cause analysis")
    corrective_action: Optional[str] = Field(None, description="Immediate corrective actions")
    preventive_action: Optional[str] = Field(None, description="Long-term preventive actions")
    owner: Optional[str] = Field(None, description="Assigned CAPA implementation owner")
    reviewer: Optional[str] = Field(None, description="Assigned QA reviewer")
    target_completion_date: Optional[datetime] = Field(None, description="Target implementation completion date")
    effectiveness_due_date: Optional[datetime] = Field(None, description="Scheduled effectiveness review date")
    priority: str = Field("Medium", description="Priority level: Critical, High, Medium, Low")
    risk_level: str = Field("Medium", description="Risk assessment: High, Medium, Low")


class CAPAUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=255)
    description: Optional[str] = Field(None, min_length=5)
    root_cause: Optional[str] = None
    corrective_action: Optional[str] = None
    preventive_action: Optional[str] = None
    owner: Optional[str] = None
    reviewer: Optional[str] = None
    effectiveness_check: Optional[str] = None
    target_completion_date: Optional[datetime] = None
    effectiveness_due_date: Optional[datetime] = None
    priority: Optional[str] = None
    risk_level: Optional[str] = None
    status: Optional[str] = Field(
        None,
        description="Allowed statuses: OPEN, UNDER_IMPLEMENTATION, PENDING_EFFECTIVENESS, EFFECTIVE, INEFFECTIVE, CLOSED, CANCELLED",
    )


class CAPAEffectivenessReview(BaseModel):
    password: str = Field(..., description="Password re-authentication for 21 CFR Part 11 signature")
    effectiveness_check: str = Field(..., min_length=5, description="Evaluation findings and evidence")
    is_effective: bool = Field(..., description="True for EFFECTIVE, False for INEFFECTIVE")
    reason: str = Field(..., min_length=10, description="21 CFR Part 11 regulatory justification")


class CAPACloseRequest(BaseModel):
    password: str = Field(..., description="Password re-authentication for 21 CFR Part 11 signature")
    reason: str = Field(..., min_length=10, description="21 CFR Part 11 closure justification")


class CAPARead(BaseModel):
    id: UUID
    complaint_id: UUID
    complaint_number: Optional[str] = None
    capa_number: str
    title: str
    description: str
    root_cause: Optional[str] = None
    corrective_action: Optional[str] = None
    preventive_action: Optional[str] = None
    owner: Optional[str] = None
    reviewer: Optional[str] = None
    effectiveness_check: Optional[str] = None
    effectiveness_due_date: Optional[datetime] = None
    target_completion_date: Optional[datetime] = None
    completed_date: Optional[datetime] = None
    priority: str
    risk_level: str
    status: str
    created_by: str
    updated_by: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CAPAListResponse(BaseModel):
    items: List[CAPARead]
    total: int
    page: int
    page_size: int
    total_pages: int


class CAPATrendItem(BaseModel):
    month: str
    created: int
    closed: int


class CAPADashboardRead(BaseModel):
    open_capas: int
    overdue_capas: int
    pending_effectiveness: int
    closed_this_month: int
    average_closure_days: float
    by_status: dict[str, int]
    by_priority: dict[str, int]
    by_risk_level: dict[str, int]
    monthly_trends: List[CAPATrendItem]
