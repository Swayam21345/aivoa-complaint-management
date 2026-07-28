from datetime import date, datetime
from typing import Any, Dict, Literal, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.complaint_history import ComplaintHistoryRead
from app.schemas.electronic_signature import ElectronicSignatureRead
from app.schemas.reviewer_note import ReviewerNoteRead
from app.schemas.uploaded_document import UploadedDocumentRead

# ─── Enums (as Literals for Pydantic v2 compatibility) ────────────────────────

RiskLevel = Literal["High", "Medium", "Low"]
Priority = Literal["Critical", "High", "Medium", "Low"]
ComplaintStatus = Literal[
    "NEW",
    "TRIAGED",
    "ASSIGNED",
    "UNDER_INVESTIGATION",
    "ROOT_CAUSE_IDENTIFIED",
    "CAPA_IN_PROGRESS",
    "QA_REVIEW",
    "QA_APPROVED",
    "CLOSED",
    "REJECTED",
    "ON_HOLD",
    "CANCELLED",
    "UNDER_REVIEW",
    "IN_PROGRESS",
    "WAITING_CUSTOMER",
    "RESOLVED",
    "Draft",
    "Under Review",
    "Closed",
]
SLAStatus = Literal["ON_TRACK", "AT_RISK", "BREACHED"]
ComplaintCategory = Literal[
    "Product Quality Defect",
    "Packaging Defect",
    "Labeling Error",
    "Delivery Damage",
    "Adverse Event",
    "Foreign Material",
    "Documentation Error",
    "Other",
]

# ─── Audit Event ──────────────────────────────────────────────────────────────

class AuditEventRead(BaseModel):
    id: UUID
    complaint_id: Optional[UUID] = None
    actor_email: str
    action_type: str
    description: str
    event_metadata: Optional[Dict[str, Any]] = None
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── SLA & Escalation ─────────────────────────────────────────────────────────

class SLATrackingRead(BaseModel):
    created_at: datetime
    due_date: datetime
    sla_status: SLAStatus
    remaining_hours: float
    age_hours: float
    time_under_review_hours: float
    sla_target_hours: float
    hours_until_due: float
    is_overdue: bool
    near_sla: bool
    is_escalated: bool
    escalation_reason: Optional[str] = None
    escalated_at: Optional[datetime] = None


# ─── Assignment ──────────────────────────────────────────────────────────────

class ComplaintAssignRequest(BaseModel):
    assigned_to: str = Field(..., max_length=255, description="Investigator full name or email")


# ─── AI Analysis ──────────────────────────────────────────────────────────────

class AIAnalysisSchema(BaseModel):
    """Structured output from the LangGraph AI workflow."""

    complaint_summary: Optional[str] = None
    product_name: Optional[str] = None
    batch_number: Optional[str] = None
    customer_name: Optional[str] = None
    category: Optional[str] = None
    risk_level: Optional[str] = None
    root_cause_recommendation: Optional[str] = None
    capa_recommendation: Optional[str] = None
    processing_time_ms: Optional[int] = None
    model_used: Optional[str] = None

    # Extended Phase 3.1 structured fields
    summary: Optional[Dict[str, Any]] = None
    completeness: Optional[Dict[str, Any]] = None
    root_cause: Optional[Dict[str, Any]] = None
    capa: Optional[Dict[str, Any]] = None
    duplicates: Optional[Dict[str, Any]] = None
    risk_explanation: Optional[Dict[str, Any]] = None

    model_config = {"protected_namespaces": ()}


class AIAnalysisRead(AIAnalysisSchema):
    """AI analysis as stored in the database (includes DB-managed fields)."""

    id: UUID
    complaint_id: UUID
    raw_llm_response: Optional[Dict[str, Any]] = None
    created_at: datetime

    model_config = {"from_attributes": True, "protected_namespaces": ()}


# ─── Complaint ────────────────────────────────────────────────────────────────

class ComplaintCreate(BaseModel):
    """Request body for POST /api/complaints."""

    product_name: Optional[str] = Field(default=None, max_length=255)
    batch_number: Optional[str] = Field(default=None, max_length=100)
    customer_name: Optional[str] = Field(default=None, max_length=255)
    category: Optional[str] = Field(default=None, max_length=100)
    risk_level: Optional[str] = Field(default=None, max_length=10)
    priority: Optional[str] = Field(default=None, max_length=20)
    status: Optional[ComplaintStatus] = Field(default="NEW")
    complaint_text: Optional[str] = None
    reviewer_notes: Optional[str] = None
    submitted_by: Optional[str] = Field(default=None, max_length=255)
    ai_analysis: Optional[AIAnalysisSchema] = None


class ComplaintUpdate(BaseModel):
    """Request body for PATCH /api/complaints/{id}."""

    status: Optional[ComplaintStatus] = None
    priority: Optional[Priority] = None
    product_name: Optional[str] = Field(default=None, max_length=255)
    batch_number: Optional[str] = Field(default=None, max_length=100)
    customer_name: Optional[str] = Field(default=None, max_length=255)
    category: Optional[str] = Field(default=None, max_length=100)
    risk_level: Optional[RiskLevel] = None
    complaint_text: Optional[str] = None
    reviewer_notes: Optional[str] = None
    changed_by: Optional[str] = Field(default=None, max_length=255)
    change_reason: Optional[str] = None


class ComplaintCreateResponse(BaseModel):
    """Minimal response after creating a complaint."""

    complaint_id: str
    id: UUID
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ComplaintUpdateResponse(BaseModel):
    """Response after patching a complaint."""

    id: UUID
    complaint_id: str
    status: str
    updated_at: datetime

    model_config = {"from_attributes": True}


class ComplaintListItem(BaseModel):
    """Single row in the paginated complaints list."""

    id: UUID
    complaint_id: str
    date_received: date
    product_name: Optional[str] = None
    customer_name: Optional[str] = None
    category: Optional[str] = None
    risk_level: Optional[str] = None
    priority: Optional[str] = None
    status: str
    assigned_to: Optional[str] = None
    assigned_by: Optional[str] = None
    assigned_at: Optional[datetime] = None
    is_escalated: bool = False
    escalated_at: Optional[datetime] = None
    escalation_reason: Optional[str] = None
    sla_tracking: Optional[SLATrackingRead] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PaginatedComplaints(BaseModel):
    """Paginated response for GET /api/complaints."""

    total: int
    page: int
    page_size: int
    items: list[ComplaintListItem]


class ComplaintDetail(BaseModel):
    """Full complaint record returned by GET /api/complaints/{id}."""

    id: UUID
    complaint_id: str
    date_received: date
    status: str
    priority: Optional[str] = None
    product_name: Optional[str] = None
    batch_number: Optional[str] = None
    customer_name: Optional[str] = None
    category: Optional[str] = None
    risk_level: Optional[str] = None
    complaint_text: Optional[str] = None
    reviewer_notes: Optional[str] = None
    submitted_by: Optional[str] = None
    assigned_to: Optional[str] = None
    assigned_by: Optional[str] = None
    assigned_at: Optional[datetime] = None
    due_date: Optional[datetime] = None
    is_escalated: bool = False
    escalated_at: Optional[datetime] = None
    escalation_reason: Optional[str] = None
    sla_tracking: Optional[SLATrackingRead] = None
    created_at: datetime
    updated_at: datetime
    ai_analysis: Optional[AIAnalysisRead] = None
    history: list[ComplaintHistoryRead] = Field(default_factory=list)
    notes: list[ReviewerNoteRead] = Field(default_factory=list)
    uploaded_documents: list[UploadedDocumentRead] = Field(default_factory=list)
    audit_events: list[AuditEventRead] = Field(default_factory=list)
    signatures: list[ElectronicSignatureRead] = Field(default_factory=list)

    model_config = {"from_attributes": True}


# ─── Investigator Dashboard ───────────────────────────────────────────────────

class InvestigatorDashboardRead(BaseModel):
    assigned_to_me: int
    pending_reviews: int
    overdue_cases: int
    completed_this_month: int
    average_resolution_time: float = Field(default=0.0, description="Average resolution time in hours")
