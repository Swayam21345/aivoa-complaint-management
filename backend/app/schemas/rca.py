from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class FiveWhyItem(BaseModel):
    step: int = Field(..., ge=1, le=5)
    question: str = Field(..., min_length=2)
    answer: str = Field(..., min_length=2)


class FishboneCategories(BaseModel):
    manpower: Optional[List[str]] = Field(default_factory=list)
    machine: Optional[List[str]] = Field(default_factory=list)
    material: Optional[List[str]] = Field(default_factory=list)
    method: Optional[List[str]] = Field(default_factory=list)
    measurement: Optional[List[str]] = Field(default_factory=list)
    milieu: Optional[List[str]] = Field(default_factory=list)


class FMEAAssessmentCreate(BaseModel):
    failure_mode: str = Field(..., min_length=3, max_length=255)
    effect_of_failure: str = Field(..., min_length=5)
    severity: int = Field(..., ge=1, le=10, description="Severity rating 1-10")
    occurrence: int = Field(..., ge=1, le=10, description="Occurrence rating 1-10")
    detection: int = Field(..., ge=1, le=10, description="Detection rating 1-10")
    recommended_action: Optional[str] = None


class FMEAAssessmentRead(BaseModel):
    id: UUID
    rca_id: UUID
    complaint_id: UUID
    failure_mode: str
    effect_of_failure: str
    severity: int
    occurrence: int
    detection: int
    rpn: int
    risk_class: str
    recommended_action: Optional[str] = None
    action_taken: Optional[str] = None
    revised_severity: Optional[int] = None
    revised_occurrence: Optional[int] = None
    revised_detection: Optional[int] = None
    revised_rpn: Optional[int] = None
    created_by: str
    updated_by: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RCACreate(BaseModel):
    complaint_id: UUID = Field(..., description="UUID of complaint")
    primary_root_cause: str = Field(..., min_length=5, description="Primary root cause finding")
    root_cause_category: str = Field(
        "Equipment Failure",
        description="Categories: Equipment Failure, Human Error, Raw Material Defect, SOP Non-compliance, Environmental",
    )
    methodology: str = Field("HYBRID", description="FIVE_WHYS, FISHBONE, or HYBRID")
    five_whys: Optional[List[FiveWhyItem]] = None
    fishbone: Optional[FishboneCategories] = None
    contributing_factors: Optional[str] = None
    fmea_items: Optional[List[FMEAAssessmentCreate]] = None


class RCAUpdate(BaseModel):
    primary_root_cause: Optional[str] = Field(None, min_length=5)
    root_cause_category: Optional[str] = None
    methodology: Optional[str] = None
    five_whys: Optional[List[FiveWhyItem]] = None
    fishbone: Optional[FishboneCategories] = None
    contributing_factors: Optional[str] = None
    status: Optional[str] = Field(None, description="DRAFT, UNDER_REVIEW, APPROVED, REJECTED")


class RCAApproveRequest(BaseModel):
    password: str = Field(..., description="Password re-authentication for 21 CFR Part 11 signature")
    reason: str = Field(..., min_length=10, description="21 CFR Part 11 RCA approval justification")


class RCARead(BaseModel):
    id: UUID
    complaint_id: UUID
    complaint_number: Optional[str] = None
    rca_number: str
    methodology: str
    primary_root_cause: str
    root_cause_category: str
    five_whys: Optional[List[FiveWhyItem]] = None
    fishbone: Optional[FishboneCategories] = None
    contributing_factors: Optional[str] = None
    status: str
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    created_by: str
    updated_by: str
    created_at: datetime
    updated_at: datetime
    fmea_items: List[FMEAAssessmentRead] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class RCAListResponse(BaseModel):
    items: List[RCARead]
    total: int
    page: int
    page_size: int
    total_pages: int


class RCADashboardRead(BaseModel):
    total_rcas: int
    approved_rcas: int
    pending_rcas: int
    high_risk_fmea_count: int
    average_rpn: float
    by_category: dict[str, int]
    by_methodology: dict[str, int]
