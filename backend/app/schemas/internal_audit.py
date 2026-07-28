from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


# ─── Internal Audit Base & CRUD Schemas ─────────────────────────────────────────
class InternalAuditBase(BaseModel):
    title: str = Field(..., max_length=255)
    audit_type: str = Field("INTERNAL_SOP", max_length=100)
    scope: str
    lead_auditor: str = Field(..., max_length=255)
    audit_team: Optional[str] = None
    department: str = Field("QUALITY_ASSURANCE", max_length=100)
    scheduled_start_date: datetime
    scheduled_end_date: datetime


class InternalAuditCreate(InternalAuditBase):
    pass


class InternalAuditUpdate(BaseModel):
    title: Optional[str] = None
    audit_type: Optional[str] = None
    scope: Optional[str] = None
    lead_auditor: Optional[str] = None
    audit_team: Optional[str] = None
    department: Optional[str] = None
    scheduled_start_date: Optional[datetime] = None
    scheduled_end_date: Optional[datetime] = None
    actual_start_date: Optional[datetime] = None
    actual_end_date: Optional[datetime] = None
    status: Optional[str] = None
    conclusion: Optional[str] = None


class AuditChecklistCreate(BaseModel):
    section: str = Field(..., max_length=100)
    requirement: str = Field(..., max_length=255)
    question: str
    compliance_status: str = Field("COMPLIANT", max_length=50)
    comments: Optional[str] = None
    evidence_summary: Optional[str] = None


class AuditChecklistRead(BaseModel):
    id: UUID
    audit_id: UUID
    section: str
    requirement: str
    question: str
    compliance_status: str
    comments: Optional[str] = None
    evidence_summary: Optional[str] = None

    class Config:
        from_attributes = True


class AuditFindingCreate(BaseModel):
    category: str = Field("OBSERVATION", max_length=50)
    description: str
    clause_reference: Optional[str] = Field(None, max_length=100)
    capa_id: Optional[UUID] = None


class AuditFindingRead(BaseModel):
    id: UUID
    audit_id: UUID
    finding_number: str
    category: str
    description: str
    clause_reference: Optional[str] = None
    capa_id: Optional[UUID] = None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class AuditApprovalCreate(BaseModel):
    password: str
    reason: str = Field("Internal Audit Report Review & Closure Approval", min_length=1)
    conclusion: Optional[str] = None


class InternalAuditRead(InternalAuditBase):
    id: UUID
    audit_number: str
    actual_start_date: Optional[datetime] = None
    actual_end_date: Optional[datetime] = None
    status: str
    conclusion: Optional[str] = None
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    created_by: str
    updated_by: str
    created_at: datetime
    updated_at: datetime
    checklists: List[AuditChecklistRead] = []
    findings: List[AuditFindingRead] = []

    class Config:
        from_attributes = True


# ─── Inspection Readiness Schemas ─────────────────────────────────────────────
class InspectionReadinessCreate(BaseModel):
    agency: str = Field("FDA", max_length=100)
    title: str = Field(..., max_length=255)
    description: str
    readiness_score: float = Field(100.0, ge=0.0, le=100.0)


class InspectionReadinessRead(BaseModel):
    id: UUID
    package_number: str
    agency: str
    title: str
    description: str
    readiness_score: float
    status: str
    created_by: str
    updated_by: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ─── Dashboard & Metrics Schemas ──────────────────────────────────────────────
class InternalAuditDashboardRead(BaseModel):
    total_audits: int
    planned_audits: int
    in_progress_audits: int
    closed_audits: int
    total_findings: int
    critical_findings_count: int
    open_findings_count: int
    avg_inspection_readiness_score: float
    by_department: Dict[str, int]
    by_category: Dict[str, int]
