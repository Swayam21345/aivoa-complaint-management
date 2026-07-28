"""
Complaint routes — /api/complaints

POST   /api/complaints                     → create complaint
GET    /api/complaints                     → paginated, searched & filtered list
GET    /api/complaints/{id}                → full detail
PATCH  /api/complaints/{id}                → update status / fields (logs history)
DELETE /api/complaints/{id}                → soft delete complaint
POST   /api/complaints/{id}/assign         → assign complaint to investigator
GET    /api/complaints/{id}/activity       → get audit event feed
POST   /api/complaints/{id}/notes          → create reviewer note
GET    /api/complaints/{id}/notes          → list reviewer notes
PATCH  /api/complaints/{id}/notes/{note_id}→ update reviewer note
DELETE /api/complaints/{id}/notes/{note_id}→ delete reviewer note
"""
from datetime import datetime
from typing import Any, Literal, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user, get_db, require_roles
from app.models.user import User
from app.schemas.complaint import (
    AuditEventRead,
    ComplaintAssignRequest,
    ComplaintCreate,
    ComplaintCreateResponse,
    ComplaintDetail,
    ComplaintUpdate,
    ComplaintUpdateResponse,
    PaginatedComplaints,
)
from app.schemas.reviewer_note import (
    ReviewerNoteCreate,
    ReviewerNoteRead,
    ReviewerNoteUpdate,
)
from app.services import complaint_service
from app.services.reviewer_note_service import ReviewerNoteService

router = APIRouter(prefix="/complaints", tags=["Complaints"])


@router.post(
    "",
    response_model=ComplaintCreateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new complaint record",
    description=(
        "Persists a complaint and its optional AI analysis payload. "
        "Generates a human-readable Complaint ID (CC-YYYYMMDD-NNNN) and initial history entry."
    ),
    dependencies=[Depends(require_roles("ADMIN", "QA_MANAGER"))],
)
async def create_complaint(
    payload: ComplaintCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ComplaintCreateResponse:
    return await complaint_service.create_complaint(db, payload, creator_email=current_user.email)


@router.get(
    "",
    response_model=PaginatedComplaints,
    summary="List complaints (paginated, searchable, filterable)",
    description=(
        "Returns a paginated list of active complaints. "
        "Filter by complaint_id, customer_name, category, priority, risk_level, status, created/updated dates, "
        "or perform partial text search across complaint text and metadata."
    ),
    dependencies=[Depends(require_roles("ADMIN", "QA_MANAGER", "INVESTIGATOR", "VIEWER"))],
)
async def list_complaints(
    complaint_id: Optional[str] = Query(default=None, alias="complaint_id"),
    customer_name: Optional[str] = Query(default=None, alias="customer_name"),
    category: Optional[str] = Query(default=None),
    priority: Optional[str] = Query(default=None, description="Critical | High | Medium | Low"),
    risk_level: Optional[str] = Query(default=None, alias="risk_level", description="High | Medium | Low"),
    status_filter: Optional[str] = Query(default=None, alias="status"),
    created_date_from: Optional[datetime] = Query(default=None),
    created_date_to: Optional[datetime] = Query(default=None),
    updated_date_from: Optional[datetime] = Query(default=None),
    updated_date_to: Optional[datetime] = Query(default=None),
    search: Optional[str] = Query(default=None, description="Partial text search query"),
    sort: Literal["created_at_asc", "created_at_desc", "updated_at_asc", "updated_at_desc"] = Query(
        default="created_at_desc",
        description="Sort order",
    ),
    sort_by: Optional[str] = Query(default=None, description="Field name to sort by"),
    sort_order: Optional[Literal["asc", "desc"]] = Query(default=None, description="Sort direction"),
    page: int = Query(default=1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(default=20, ge=1, le=100, description="Records per page (max 100)"),
    db: AsyncSession = Depends(get_db),
) -> PaginatedComplaints:
    return await complaint_service.list_complaints(
        db,
        complaint_id_filter=complaint_id,
        customer_name_filter=customer_name,
        category_filter=category,
        priority_filter=priority,
        risk_level_filter=risk_level,
        status_filter=status_filter,
        created_date_from=created_date_from,
        created_date_to=created_date_to,
        updated_date_from=updated_date_from,
        updated_date_to=updated_date_to,
        search=search,
        sort=sort,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order,
    )


@router.get(
    "/{complaint_id}",
    response_model=ComplaintDetail,
    summary="Get full complaint detail",
    description="Returns a single complaint record including AI analysis, audit history, notes, and documents. Raises 404 if not found.",
    dependencies=[Depends(require_roles("ADMIN", "QA_MANAGER", "INVESTIGATOR", "VIEWER"))],
)
async def get_complaint(
    complaint_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> ComplaintDetail:
    return await complaint_service.get_complaint(db, complaint_id)


@router.post(
    "/{complaint_id}/assign",
    response_model=ComplaintDetail,
    summary="Assign complaint to an Investigator",
    description="Assigns complaint to an Investigator and logs audit metadata. Only ADMIN and QA_MANAGER allowed.",
    dependencies=[Depends(require_roles("ADMIN", "QA_MANAGER"))],
)
async def assign_complaint(
    complaint_id: UUID,
    payload: ComplaintAssignRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ComplaintDetail:
    return await complaint_service.assign_complaint(db, complaint_id, payload.assigned_to, current_user)


@router.get(
    "/{complaint_id}/activity",
    response_model=list[AuditEventRead],
    summary="Get complaint activity audit feed",
    description="Returns immutable audit trail of actions performed on this complaint.",
    dependencies=[Depends(require_roles("ADMIN", "QA_MANAGER", "INVESTIGATOR", "VIEWER"))],
)
async def get_complaint_activity(
    complaint_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> list[AuditEventRead]:
    complaint = await complaint_service.get_complaint(db, complaint_id)
    return complaint.audit_events


@router.patch(
    "/{complaint_id}",
    response_model=ComplaintUpdateResponse,
    summary="Update complaint status or fields",
    description="Partially updates complaint fields. Enforces strict state machine validation for status transitions.",
    dependencies=[Depends(require_roles("ADMIN", "QA_MANAGER", "INVESTIGATOR"))],
)
async def update_complaint(
    complaint_id: UUID,
    payload: ComplaintUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ComplaintUpdateResponse:
    return await complaint_service.update_complaint(
        db,
        complaint_id,
        payload,
        actor_email=current_user.email,
        actor_role=current_user.role,
    )


@router.delete(
    "/{complaint_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Soft delete a complaint",
    description="Marks a complaint record as soft-deleted (is_deleted = True).",
    dependencies=[Depends(require_roles("ADMIN"))],
)
async def delete_complaint(
    complaint_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Response:
    await complaint_service.delete_complaint(db, complaint_id, actor_email=current_user.email)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ─── Phase 3.2 Copilot, Timeline & Export Endpoints ───────────────────────────

@router.get(
    "/{complaint_id}/copilot",
    summary="Get aggregated AI Copilot explainability results",
    description="Returns aggregated AI model reasoning, confidence scores, root cause, and CAPA without re-invoking LLM.",
    dependencies=[Depends(require_roles("ADMIN", "QA_MANAGER", "INVESTIGATOR", "VIEWER"))],
)
async def get_copilot_explainability(
    complaint_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    return await complaint_service.get_copilot_explainability(db, complaint_id)


@router.get(
    "/{complaint_id}/timeline",
    summary="Get complaint audit timeline",
    description="Returns chronological sequence of events including creation, AI analysis, status updates, and notes.",
    dependencies=[Depends(require_roles("ADMIN", "QA_MANAGER", "INVESTIGATOR", "VIEWER"))],
)
async def get_complaint_timeline(
    complaint_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    return await complaint_service.get_complaint_timeline(db, complaint_id)


@router.get(
    "/{complaint_id}/export/pdf",
    summary="Export complaint report as PDF",
    description="Generates a professional pharmaceutical QMS PDF report using ReportLab.",
    dependencies=[Depends(require_roles("ADMIN", "QA_MANAGER", "INVESTIGATOR", "VIEWER"))],
)
async def export_complaint_pdf(
    complaint_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Response:
    pdf_bytes = await complaint_service.export_complaint_pdf(db, complaint_id, actor_email=current_user.email)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=Complaint_Report_{complaint_id}.pdf"
        },
    )


# ─── Reviewer Notes API ───────────────────────────────────────────────────────

@router.post(
    "/{complaint_id}/notes",
    response_model=ReviewerNoteRead,
    status_code=status.HTTP_201_CREATED,
    summary="Add a reviewer note to a complaint",
    dependencies=[Depends(require_roles("ADMIN", "QA_MANAGER", "INVESTIGATOR"))],
)
async def add_reviewer_note(
    complaint_id: UUID,
    payload: ReviewerNoteCreate,
    db: AsyncSession = Depends(get_db),
) -> ReviewerNoteRead:
    note = await ReviewerNoteService.create_note(db, complaint_id, payload)
    return ReviewerNoteRead.model_validate(note)


@router.get(
    "/{complaint_id}/notes",
    response_model=list[ReviewerNoteRead],
    summary="List all reviewer notes for a complaint",
    dependencies=[Depends(require_roles("ADMIN", "QA_MANAGER", "INVESTIGATOR", "VIEWER"))],
)
async def list_reviewer_notes(
    complaint_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> list[ReviewerNoteRead]:
    notes = await ReviewerNoteService.list_notes(db, complaint_id)
    return [ReviewerNoteRead.model_validate(n) for n in notes]


@router.patch(
    "/{complaint_id}/notes/{note_id}",
    response_model=ReviewerNoteRead,
    summary="Update a reviewer note",
    dependencies=[Depends(require_roles("ADMIN", "QA_MANAGER", "INVESTIGATOR"))],
)
async def update_reviewer_note(
    complaint_id: UUID,
    note_id: UUID,
    payload: ReviewerNoteUpdate,
    db: AsyncSession = Depends(get_db),
) -> ReviewerNoteRead:
    note = await ReviewerNoteService.update_note(db, complaint_id, note_id, payload)
    return ReviewerNoteRead.model_validate(note)


@router.delete(
    "/{complaint_id}/notes/{note_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Soft-delete a reviewer note",
    dependencies=[Depends(require_roles("ADMIN", "QA_MANAGER"))],
)
async def delete_reviewer_note(
    complaint_id: UUID,
    note_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> Response:
    await ReviewerNoteService.delete_note(db, complaint_id, note_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
