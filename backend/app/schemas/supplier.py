from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


# ─── Supplier Base & CRUD Schemas ──────────────────────────────────────────────
class SupplierBase(BaseModel):
    supplier_name: str = Field(..., max_length=255)
    supplier_type: str = Field("RAW_MATERIAL", max_length=100)
    category: str = Field("PRIMARY", max_length=100)
    risk_level: str = Field("MEDIUM", max_length=50)
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    zip_code: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None


class SupplierCreate(SupplierBase):
    pass


class SupplierUpdate(BaseModel):
    supplier_name: Optional[str] = None
    supplier_type: Optional[str] = None
    category: Optional[str] = None
    status: Optional[str] = None
    risk_level: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    zip_code: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None


class SupplierContactRead(BaseModel):
    id: UUID
    supplier_id: UUID
    name: str
    email: str
    phone: Optional[str] = None
    title: Optional[str] = None
    is_primary: bool

    class Config:
        from_attributes = True


class SupplierContactCreate(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    title: Optional[str] = None
    is_primary: bool = False


class SupplierAuditCreate(BaseModel):
    audit_type: str = Field("QUALIFICATION", max_length=50)
    scheduled_date: datetime
    auditor: str = Field(..., max_length=255)
    score: Optional[float] = None
    findings_summary: Optional[str] = None


class SupplierAuditRead(BaseModel):
    id: UUID
    supplier_id: UUID
    audit_number: str
    audit_type: str
    scheduled_date: datetime
    completed_date: Optional[datetime] = None
    auditor: str
    status: str
    score: Optional[float] = None
    findings_summary: Optional[str] = None

    class Config:
        from_attributes = True


class SupplierScorecardCreate(BaseModel):
    period: str = Field(..., max_length=50)
    quality_score: float = Field(100.0, ge=0.0, le=100.0)
    delivery_score: float = Field(100.0, ge=0.0, le=100.0)
    compliance_score: float = Field(100.0, ge=0.0, le=100.0)


class SupplierScorecardRead(BaseModel):
    id: UUID
    supplier_id: UUID
    period: str
    quality_score: float
    delivery_score: float
    compliance_score: float
    overall_score: float
    grade: str
    evaluated_by: str
    evaluated_at: datetime

    class Config:
        from_attributes = True


class SupplierNonconformanceCreate(BaseModel):
    complaint_id: Optional[UUID] = None
    title: str = Field(..., max_length=255)
    description: str
    severity: str = Field("MEDIUM", max_length=50)


class SupplierNonconformanceRead(BaseModel):
    id: UUID
    supplier_id: UUID
    complaint_id: Optional[UUID] = None
    ncr_number: str
    title: str
    description: str
    severity: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class SupplierCorrectiveActionCreate(BaseModel):
    capa_id: Optional[UUID] = None
    action_plan: str
    owner: str = Field(..., max_length=255)
    due_days: int = Field(30, ge=1)


class SupplierCorrectiveActionRead(BaseModel):
    id: UUID
    supplier_id: UUID
    capa_id: Optional[UUID] = None
    action_number: str
    action_plan: str
    owner: str
    due_date: datetime
    status: str
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class SupplierApprovalCreate(BaseModel):
    password: str
    reason: str = Field("Supplier Qualification & Quality Agreement Approval", min_length=1)


class SupplierRead(SupplierBase):
    id: UUID
    supplier_number: str
    status: str
    approval_status: str
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    created_by: str
    updated_by: str
    created_at: datetime
    updated_at: datetime
    contacts: List[SupplierContactRead] = []
    audits: List[SupplierAuditRead] = []
    scorecards: List[SupplierScorecardRead] = []
    nonconformances: List[SupplierNonconformanceRead] = []
    corrective_actions: List[SupplierCorrectiveActionRead] = []

    class Config:
        from_attributes = True


# ─── Dashboard & Reports Schemas ──────────────────────────────────────────────
class SupplierDashboardRead(BaseModel):
    total_suppliers: int
    approved_suppliers: int
    pending_approvals: int
    disqualified_suppliers: int
    risk_distribution: Dict[str, int]
    status_distribution: Dict[str, int]
    by_type: Dict[str, int]
    upcoming_audits_count: int
    open_supplier_capas_count: int
    avg_overall_score: float


class SupplierReportRead(BaseModel):
    total_suppliers: int
    approved_count: int
    high_risk_count: int
    open_ncr_count: int
    suppliers: List[SupplierRead]
