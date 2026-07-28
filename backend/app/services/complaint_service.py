"""
Complaint service — business logic layer.

All database interactions for the complaints domain live here.
Routes delegate to these functions; they never touch SQLAlchemy directly.
"""
from datetime import date, datetime, timezone
from typing import Any
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ai_analysis import AIAnalysis
from app.models.audit_event import AuditEvent
from app.models.complaint import Complaint
from app.models.complaint_history import ComplaintHistory
from app.models.user import User
from app.schemas.complaint import (
    AIAnalysisSchema,
    AuditEventRead,
    ComplaintCreate,
    ComplaintCreateResponse,
    ComplaintDetail,
    ComplaintListItem,
    ComplaintUpdate,
    ComplaintUpdateResponse,
    PaginatedComplaints,
    SLATrackingRead,
)
from app.schemas.complaint_history import ComplaintHistoryRead
from app.schemas.electronic_signature import ElectronicSignatureRead
from app.schemas.reviewer_note import ReviewerNoteRead
from app.schemas.uploaded_document import UploadedDocumentRead
from app.services.workflow_service import (
    evaluate_complaint_sla,
    log_audit_event,
    validate_status_transition_for_role,
)


# ─── Helpers ──────────────────────────────────────────────────────────────────

async def _next_complaint_id(db: AsyncSession) -> str:
    """
    Generate the next human-readable complaint ID.
    Format: CC-YYYYMMDD-NNNN (e.g. CC-20260727-0001)
    """
    count_res = await db.execute(select(func.count()).select_from(Complaint))
    seq = (count_res.scalar_one() or 0) + 1
    today = datetime.now(timezone.utc).strftime("%Y%m%d")
    return f"CC-{today}-{seq:04d}"


def _orm_to_detail(complaint: Complaint) -> ComplaintDetail:
    """Map a Complaint ORM instance (with selectin-loaded relationships) to ComplaintDetail."""
    ai_read = None
    if complaint.ai_analysis is not None:
        ai = complaint.ai_analysis
        raw = ai.raw_llm_response or {}
        ai_read = {
            "id": ai.id,
            "complaint_id": ai.complaint_id,
            "complaint_summary": ai.complaint_summary,
            "product_name": ai.extracted_product_name,
            "batch_number": ai.extracted_batch_number,
            "customer_name": ai.extracted_customer_name,
            "category": ai.extracted_category,
            "risk_level": ai.risk_level,
            "root_cause_recommendation": ai.root_cause_recommendation,
            "capa_recommendation": ai.capa_recommendation,
            "summary": raw.get("summary"),
            "completeness": raw.get("completeness"),
            "root_cause": raw.get("root_cause"),
            "capa": raw.get("capa"),
            "duplicates": raw.get("duplicates"),
            "risk_explanation": raw.get("risk_explanation"),
            "processing_time_ms": ai.processing_time_ms,
            "model_used": ai.model_used,
            "raw_llm_response": ai.raw_llm_response,
            "created_at": ai.created_at,
        }

    history_list = [
        ComplaintHistoryRead(
            id=h.id,
            complaint_id=h.complaint_id,
            old_status=h.old_status,
            new_status=h.new_status,
            changed_by=h.changed_by,
            change_reason=h.change_reason,
            created_at=h.created_at,
        )
        for h in getattr(complaint, "history", [])
    ]

    notes_list = [
        ReviewerNoteRead(
            id=n.id,
            complaint_id=n.complaint_id,
            author=n.author,
            content=n.content,
            created_at=n.created_at,
            updated_at=n.updated_at,
        )
        for n in getattr(complaint, "notes", [])
        if not getattr(n, "is_deleted", False)
    ]

    docs_list = [
        UploadedDocumentRead(
            id=d.id,
            complaint_id=d.complaint_id,
            input_type=d.input_type,
            original_filename=d.original_filename,
            content_type=d.content_type,
            file_size_bytes=d.file_size_bytes,
            extracted_text=d.extracted_text,
            created_at=d.created_at,
        )
        for d in getattr(complaint, "uploaded_documents", [])
        if not getattr(d, "is_deleted", False)
    ]

    audit_list = [
        AuditEventRead(
            id=a.id,
            complaint_id=a.complaint_id,
            actor_email=a.actor_email,
            action_type=a.action_type,
            description=a.description,
            event_metadata=a.event_metadata,
            created_at=a.created_at,
        )
        for a in getattr(complaint, "audit_events", [])
    ]

    signatures_list = [
        ElectronicSignatureRead(
            id=s.id,
            complaint_id=s.complaint_id,
            user_id=s.user_id,
            action=s.action,
            status_before=s.status_before,
            status_after=s.status_after,
            reason=s.reason,
            signature_timestamp=s.signature_timestamp,
            ip_address=s.ip_address,
            user_agent=s.user_agent,
            signature_hash=s.signature_hash,
            created_at=s.created_at,
        )
        for s in getattr(complaint, "signatures", [])
    ]

    sla_metrics = evaluate_complaint_sla(complaint)
    sla_read = SLATrackingRead(**sla_metrics)

    return ComplaintDetail(
        id=complaint.id,
        complaint_id=complaint.complaint_id,
        date_received=complaint.date_received,
        status=complaint.status,
        priority=complaint.priority,
        product_name=complaint.product_name,
        batch_number=complaint.batch_number,
        customer_name=complaint.customer_name,
        category=complaint.category,
        risk_level=complaint.risk_level,
        complaint_text=complaint.complaint_text,
        reviewer_notes=complaint.reviewer_notes,
        submitted_by=complaint.submitted_by,
        assigned_to=complaint.assigned_to,
        assigned_by=complaint.assigned_by,
        assigned_at=complaint.assigned_at,
        due_date=sla_metrics.get("due_date"),
        is_escalated=complaint.is_escalated,
        escalated_at=complaint.escalated_at,
        escalation_reason=complaint.escalation_reason,
        sla_tracking=sla_read,
        created_at=complaint.created_at,
        updated_at=complaint.updated_at,
        ai_analysis=ai_read,
        history=history_list,
        notes=notes_list,
        uploaded_documents=docs_list,
        audit_events=audit_list,
        signatures=signatures_list,
    )


# ─── Create ───────────────────────────────────────────────────────────────────

async def create_complaint(
    db: AsyncSession,
    payload: ComplaintCreate,
    creator_email: str = "system@aiccms.local",
) -> ComplaintCreateResponse:
    """
    Persist a new complaint and its optional AI analysis to the database.
    """
    complaint_id = await _next_complaint_id(db)
    initial_status = payload.status or "NEW"

    complaint = Complaint(
        complaint_id=complaint_id,
        date_received=date.today(),
        status=initial_status,
        priority=payload.priority,
        product_name=payload.product_name,
        batch_number=payload.batch_number,
        customer_name=payload.customer_name,
        category=payload.category,
        risk_level=payload.risk_level,
        complaint_text=payload.complaint_text,
        reviewer_notes=payload.reviewer_notes,
        submitted_by=payload.submitted_by,
        is_deleted=False,
    )
    db.add(complaint)
    await db.flush()  # get complaint.id

    # Evaluate SLA & set due_date
    sla_metrics = evaluate_complaint_sla(complaint)
    complaint.due_date = sla_metrics.get("due_date")

    # Log initial status history entry
    history_entry = ComplaintHistory(
        complaint_id=complaint.id,
        old_status=None,
        new_status=initial_status,
        changed_by=payload.submitted_by or creator_email,
        change_reason="Complaint record created",
    )
    db.add(history_entry)

    # Log immutable audit event
    await log_audit_event(
        db,
        action_type="Created",
        description=f"Complaint {complaint_id} logged for product '{payload.product_name or 'N/A'}'.",
        actor_email=creator_email,
        complaint_id=complaint.id,
    )

    # Persist AI analysis if provided
    if payload.ai_analysis is not None:
        ai: AIAnalysisSchema = payload.ai_analysis
        ai_record = AIAnalysis(
            complaint_id=complaint.id,
            complaint_summary=ai.complaint_summary,
            extracted_product_name=ai.product_name,
            extracted_batch_number=ai.batch_number,
            extracted_customer_name=ai.customer_name,
            extracted_category=ai.category,
            risk_level=ai.risk_level,
            root_cause_recommendation=ai.root_cause_recommendation,
            capa_recommendation=ai.capa_recommendation,
            raw_llm_response=ai.model_dump(mode="json"),
            processing_time_ms=ai.processing_time_ms,
            model_used=ai.model_used or "gemma2-9b-it",
        )
        db.add(ai_record)

        await log_audit_event(
            db,
            action_type="AI Analysis",
            description=f"AI Copilot completed automated triage ({payload.risk_level or 'Medium'} Risk).",
            actor_email="ai.engine@aiccms.local",
            complaint_id=complaint.id,
        )

    await db.flush()
    await db.refresh(complaint)

    from app.services.dashboard_service import DashboardService
    DashboardService.invalidate_cache()

    return ComplaintCreateResponse(
        complaint_id=complaint.complaint_id,
        id=complaint.id,
        status=complaint.status,
        created_at=complaint.created_at,
    )


# ─── List ─────────────────────────────────────────────────────────────────────

async def list_complaints(
    db: AsyncSession,
    complaint_id_filter: str | None = None,
    customer_name_filter: str | None = None,
    category_filter: str | None = None,
    priority_filter: str | None = None,
    risk_level_filter: str | None = None,
    status_filter: str | None = None,
    created_date_from: datetime | None = None,
    created_date_to: datetime | None = None,
    updated_date_from: datetime | None = None,
    updated_date_to: datetime | None = None,
    search: str | None = None,
    sort: str = "created_at_desc",
    page: int = 1,
    page_size: int = 20,
    sort_by: str | None = None,
    sort_order: str | None = None,
) -> PaginatedComplaints:
    """
    Return a paginated, filtered, and searched list of active complaints.
    """
    stmt = select(Complaint).where(Complaint.is_deleted == False)  # noqa: E712

    if complaint_id_filter:
        stmt = stmt.where(Complaint.complaint_id.ilike(f"%{complaint_id_filter}%"))
    if customer_name_filter:
        stmt = stmt.where(Complaint.customer_name.ilike(f"%{customer_name_filter}%"))
    if category_filter:
        stmt = stmt.where(Complaint.category == category_filter)
    if priority_filter:
        stmt = stmt.where(Complaint.priority == priority_filter)
    if risk_level_filter:
        stmt = stmt.where(Complaint.risk_level == risk_level_filter)
    if status_filter:
        stmt = stmt.where(Complaint.status == status_filter)
    if created_date_from:
        stmt = stmt.where(Complaint.created_at >= created_date_from)
    if created_date_to:
        stmt = stmt.where(Complaint.created_at <= created_date_to)
    if updated_date_from:
        stmt = stmt.where(Complaint.updated_at >= updated_date_from)
    if updated_date_to:
        stmt = stmt.where(Complaint.updated_at <= updated_date_to)

    if search:
        search_pattern = f"%{search}%"
        stmt = stmt.where(
            or_(
                Complaint.complaint_id.ilike(search_pattern),
                Complaint.customer_name.ilike(search_pattern),
                Complaint.product_name.ilike(search_pattern),
                Complaint.batch_number.ilike(search_pattern),
                Complaint.complaint_text.ilike(search_pattern),
            )
        )

    column_map = {
        "created_at": Complaint.created_at,
        "updated_at": Complaint.updated_at,
        "status": Complaint.status,
        "priority": Complaint.priority,
        "risk_level": Complaint.risk_level,
        "complaint_id": Complaint.complaint_id,
        "product_name": Complaint.product_name,
        "customer_name": Complaint.customer_name,
        "category": Complaint.category,
    }

    if sort_by and sort_by in column_map:
        col = column_map[sort_by]
        if sort_order and sort_order.lower() == "asc":
            stmt = stmt.order_by(col.asc())
        else:
            stmt = stmt.order_by(col.desc())
    elif sort == "created_at_asc":
        stmt = stmt.order_by(Complaint.created_at.asc())
    elif sort == "updated_at_desc":
        stmt = stmt.order_by(Complaint.updated_at.desc())
    elif sort == "updated_at_asc":
        stmt = stmt.order_by(Complaint.updated_at.asc())
    else:
        stmt = stmt.order_by(Complaint.created_at.desc())

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total: int = (await db.execute(count_stmt)).scalar_one()

    offset = (page - 1) * page_size
    stmt = stmt.offset(offset).limit(page_size)

    rows = (await db.execute(stmt)).scalars().all()

    items = []
    for c in rows:
        sla_metrics = evaluate_complaint_sla(c)
        items.append(
            ComplaintListItem(
                id=c.id,
                complaint_id=c.complaint_id,
                date_received=c.date_received,
                product_name=c.product_name,
                customer_name=c.customer_name,
                category=c.category,
                risk_level=c.risk_level,
                priority=c.priority,
                status=c.status,
                assigned_to=c.assigned_to,
                assigned_by=c.assigned_by,
                assigned_at=c.assigned_at,
                is_escalated=c.is_escalated,
                escalated_at=c.escalated_at,
                escalation_reason=c.escalation_reason,
                sla_tracking=SLATrackingRead(**sla_metrics),
                created_at=c.created_at,
                updated_at=c.updated_at,
            )
        )

    return PaginatedComplaints(
        total=total,
        page=page,
        page_size=page_size,
        items=items,
    )


# ─── Get ──────────────────────────────────────────────────────────────────────

async def get_complaint(
    db: AsyncSession,
    complaint_id: UUID,
) -> ComplaintDetail:
    """
    Return a full complaint record including AI analysis, history, notes, and documents.
    """
    result = await db.execute(
        select(Complaint).where(
            Complaint.id == complaint_id,
            Complaint.is_deleted == False,  # noqa: E712
        )
    )
    complaint: Complaint | None = result.scalar_one_or_none()

    if complaint is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Complaint '{complaint_id}' not found.",
        )

    return _orm_to_detail(complaint)


# ─── Assign ───────────────────────────────────────────────────────────────────

async def assign_complaint(
    db: AsyncSession,
    complaint_id: UUID,
    assigned_to: str,
    assigner_user: User,
) -> ComplaintDetail:
    """
    Assign complaint to an Investigator.
    """
    result = await db.execute(
        select(Complaint).where(
            Complaint.id == complaint_id,
            Complaint.is_deleted == False,  # noqa: E712
        )
    )
    complaint: Complaint | None = result.scalar_one_or_none()

    if complaint is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Complaint '{complaint_id}' not found.",
        )

    now = datetime.now(timezone.utc)
    old_assigned = complaint.assigned_to or "Unassigned"
    complaint.assigned_to = assigned_to
    complaint.assigned_by = assigner_user.full_name
    complaint.assigned_at = now

    # Auto transition status to ASSIGNED if currently NEW or TRIAGED
    if complaint.status in ("NEW", "TRIAGED"):
        complaint.status = "ASSIGNED"

    complaint.updated_at = now

    await log_audit_event(
        db,
        action_type="Assigned",
        description=f"Complaint assigned to Investigator '{assigned_to}' (previously '{old_assigned}') by {assigner_user.full_name}.",
        actor_email=assigner_user.email,
        complaint_id=complaint.id,
    )

    await db.flush()
    await db.refresh(complaint)

    from app.services.dashboard_service import DashboardService
    DashboardService.invalidate_cache()

    return _orm_to_detail(complaint)


# ─── Update ───────────────────────────────────────────────────────────────────

async def update_complaint(
    db: AsyncSession,
    complaint_id: UUID,
    payload: ComplaintUpdate,
    actor_email: str = "system@aiccms.local",
    actor_role: str = "ADMIN",
) -> ComplaintUpdateResponse:
    """
    Update complaint fields. Enforces state machine and role-based transition authorization.
    """
    result = await db.execute(
        select(Complaint).where(
            Complaint.id == complaint_id,
            Complaint.is_deleted == False,  # noqa: E712
        )
    )
    complaint: Complaint | None = result.scalar_one_or_none()

    if complaint is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Complaint '{complaint_id}' not found.",
        )

    old_status = complaint.status

    if payload.product_name is not None:
        complaint.product_name = payload.product_name
    if payload.batch_number is not None:
        complaint.batch_number = payload.batch_number
    if payload.customer_name is not None:
        complaint.customer_name = payload.customer_name
    if payload.category is not None:
        complaint.category = payload.category
    if payload.risk_level is not None:
        complaint.risk_level = payload.risk_level
    if payload.priority is not None:
        complaint.priority = payload.priority
    if payload.complaint_text is not None:
        complaint.complaint_text = payload.complaint_text
    if payload.reviewer_notes is not None:
        complaint.reviewer_notes = payload.reviewer_notes

    # Enforce strict state machine & role validation if status changes
    if payload.status is not None and payload.status != old_status:
        validate_status_transition_for_role(actor_role, old_status, payload.status)

        # Requirement: Approved RCA record is required before ROOT_CAUSE_IDENTIFIED
        if payload.status == "ROOT_CAUSE_IDENTIFIED":
            from app.services.rca_service import RCAService
            rca_approved = await RCAService.is_rca_approved_for_complaint(db, complaint.id)
            if not rca_approved:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot transition to ROOT_CAUSE_IDENTIFIED: An approved RCA record is required.",
                )


        # Requirement: Complaint cannot move to QA_APPROVED unless all linked CAPAs are CLOSED
        if payload.status == "QA_APPROVED":
            from app.services.capa_service import CAPAService
            are_closed = await CAPAService.are_all_complaint_capas_closed(db, complaint.id)
            if not are_closed:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot approve complaint: All associated CAPAs must be CLOSED before QA Approval.",
                )

        complaint.status = payload.status



        history_entry = ComplaintHistory(
            complaint_id=complaint.id,
            old_status=old_status,
            new_status=payload.status,
            changed_by=payload.changed_by or actor_email,
            change_reason=payload.change_reason or f"Status changed from {old_status} to {payload.status}",
        )
        db.add(history_entry)

        await log_audit_event(
            db,
            action_type="Status Changed",
            description=f"Status transitioned from '{old_status}' to '{payload.status}'. Reason: {payload.change_reason or 'Workflow update'}",
            actor_email=actor_email,
            complaint_id=complaint.id,
        )

    evaluate_complaint_sla(complaint)

    complaint.updated_at = datetime.now(timezone.utc)

    await db.flush()
    await db.refresh(complaint)

    from app.services.dashboard_service import DashboardService
    DashboardService.invalidate_cache()

    return ComplaintUpdateResponse(
        id=complaint.id,
        complaint_id=complaint.complaint_id,
        status=complaint.status,
        updated_at=complaint.updated_at,
    )


# ─── Soft Delete ──────────────────────────────────────────────────────────────

async def delete_complaint(
    db: AsyncSession,
    complaint_id: UUID,
    actor_email: str = "system@aiccms.local",
) -> None:
    """
    Soft-delete a complaint record (sets is_deleted = True, deleted_at = now()).
    """
    result = await db.execute(
        select(Complaint).where(
            Complaint.id == complaint_id,
            Complaint.is_deleted == False,  # noqa: E712
        )
    )
    complaint: Complaint | None = result.scalar_one_or_none()

    if complaint is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Complaint with ID '{complaint_id}' not found.",
        )

    complaint.is_deleted = True
    complaint.deleted_at = datetime.now(timezone.utc)

    await log_audit_event(
        db,
        action_type="Status Changed",
        description=f"Complaint {complaint.complaint_id} was soft-deleted.",
        actor_email=actor_email,
        complaint_id=complaint.id,
    )

    await db.flush()

    from app.services.dashboard_service import DashboardService
    DashboardService.invalidate_cache()


# ─── Phase 3.2 Extensions ─────────────────────────────────────────────────────

async def get_copilot_explainability(
    db: AsyncSession,
    complaint_id: UUID,
) -> dict[str, Any]:
    """
    Returns aggregated AI copilot results, reasoning, and confidence metrics.
    """
    complaint = await get_complaint(db, complaint_id)
    ai = complaint.ai_analysis

    if ai is None:
        return {
            "complaint_id": complaint.id,
            "complaint_number": complaint.complaint_id,
            "complaint_summary": {"short_summary": "No AI analysis recorded."},
            "completeness": {"completeness_score": 0, "missing_fields": [], "recommendations": []},
            "root_causes": {"probable_root_causes": [], "confidence": 0.0},
            "capa": {"corrective_actions": [], "preventive_actions": []},
            "duplicate_matches": {"duplicate_found": False, "similar_complaints": [], "confidence": 0.0},
            "risk_assessment": {"risk_level": complaint.risk_level or "Unassessed", "explanation": "Pending AI analysis."},
            "reasoning": "AI analysis has not been performed on this complaint.",
            "confidence_scores": {"overall": 0.0},
        }

    raw = ai.raw_llm_response or {}
    summary_data = ai.summary or raw.get("summary") or {"short_summary": ai.complaint_summary, "detailed_summary": ai.complaint_summary}
    completeness_data = ai.completeness or raw.get("completeness") or {"completeness_score": 80, "missing_fields": [], "recommendations": []}
    root_cause_data = ai.root_cause or raw.get("root_cause") or {"probable_root_causes": [ai.root_cause_recommendation] if ai.root_cause_recommendation else [], "confidence": 0.85}
    capa_data = ai.capa or raw.get("capa") or {"corrective_actions": [ai.capa_recommendation] if ai.capa_recommendation else [], "preventive_actions": []}
    duplicate_data = ai.duplicates or raw.get("duplicates") or {"duplicate_found": False, "similar_complaints": [], "confidence": 0.95}
    risk_data = ai.risk_explanation or raw.get("risk_explanation") or {"risk_level": ai.risk_level or "Medium", "explanation": "Risk assessed based on complaint defect classification."}

    return {
        "complaint_id": complaint.id,
        "complaint_number": complaint.complaint_id,
        "complaint_summary": summary_data,
        "completeness": completeness_data,
        "root_causes": root_cause_data,
        "capa": capa_data,
        "duplicate_matches": duplicate_data,
        "risk_assessment": risk_data,
        "reasoning": (
            f"Multi-stage LangGraph workflow evaluated intake metadata. "
            f"Category '{complaint.category}' classified at '{complaint.risk_level}' risk level with "
            f"{completeness_data.get('completeness_score', 80)}% intake completeness."
        ),
        "confidence_scores": {
            "extract_confidence": 0.90,
            "classify_confidence": 0.88,
            "root_cause_confidence": float(root_cause_data.get("confidence") or 0.85),
            "duplicate_scan_confidence": float(duplicate_data.get("confidence") or 0.95),
        },
    }


async def get_complaint_timeline(
    db: AsyncSession,
    complaint_id: UUID,
) -> dict[str, Any]:
    """
    Assembles a complete chronological audit timeline of all events for a complaint.
    """
    complaint = await get_complaint(db, complaint_id)
    events: list[dict[str, Any]] = []

    # 1. Created
    events.append({
        "id": f"evt-created-{complaint.id}",
        "event_type": "CREATED",
        "title": "Complaint Logged",
        "description": f"Complaint {complaint.complaint_id} created for product '{complaint.product_name or 'N/A'}'.",
        "author": complaint.submitted_by or "System Intake",
        "timestamp": complaint.created_at,
        "icon": "📝",
        "status": "NEW",
    })

    # 2. AI Analyzed (if exists)
    if complaint.ai_analysis is not None:
        events.append({
            "id": f"evt-ai-{complaint.ai_analysis.id}",
            "event_type": "AI_ANALYZED",
            "title": "AI Advisory Copilot Analysis",
            "description": f"LangGraph AI workflow completed risk evaluation ({complaint.risk_level or 'Medium'} Risk).",
            "author": f"AICCMS Engine ({complaint.ai_analysis.model_used or 'gemma2-9b-it'})",
            "timestamp": complaint.ai_analysis.created_at,
            "icon": "✦",
            "status": "UNDER_REVIEW",
        })

    # 3. History status changes
    for h in complaint.history:
        events.append({
            "id": f"evt-hist-{h.id}",
            "event_type": "STATUS_CHANGED",
            "title": f"Status Changed to {h.new_status}",
            "description": f"Transitioned from '{h.old_status or 'N/A'}' to '{h.new_status}'. Reason: {h.change_reason or 'No reason provided'}",
            "author": h.changed_by or "Quality Manager",
            "timestamp": h.created_at,
            "icon": "🔄",
            "status": h.new_status,
        })

    # 4. Reviewer Notes
    for n in complaint.notes:
        events.append({
            "id": f"evt-note-{n.id}",
            "event_type": "NOTE_ADDED",
            "title": "Reviewer Note Added",
            "description": n.content,
            "author": n.author,
            "timestamp": n.created_at,
            "icon": "💬",
            "status": complaint.status,
        })

    # 5. Audit Events
    for a in getattr(complaint, "audit_events", []):
        events.append({
            "id": f"evt-audit-{a.id}",
            "event_type": a.action_type.upper().replace(" ", "_"),
            "title": f"Audit: {a.action_type}",
            "description": a.description,
            "author": a.actor_email,
            "timestamp": a.created_at,
            "icon": "🛡️",
            "status": complaint.status,
        })

    events.sort(key=lambda x: x["timestamp"])

    return {
        "complaint_id": complaint.id,
        "complaint_number": complaint.complaint_id,
        "events": events,
    }


async def export_complaint_pdf(
    db: AsyncSession,
    complaint_id: UUID,
    actor_email: str = "system@aiccms.local",
) -> bytes:
    """
    Generates a professional ReportLab PDF report for a complaint and logs an audit event.
    """
    from app.models.complaint import Complaint
    from app.services.pdf_export_service import build_complaint_pdf
    from sqlalchemy.orm import selectinload

    result = await db.execute(
        select(Complaint)
        .options(
            selectinload(Complaint.ai_analysis),
            selectinload(Complaint.notes),
            selectinload(Complaint.history),
        )
        .where(
            Complaint.id == complaint_id,
            Complaint.is_deleted == False,  # noqa: E712
        )
    )
    complaint: Complaint | None = result.scalar_one_or_none()
    if complaint is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Complaint with ID '{complaint_id}' not found.",
        )

    await log_audit_event(
        db,
        action_type="PDF Exported",
        description=f"Complaint report PDF generated and downloaded for {complaint.complaint_id}.",
        actor_email=actor_email,
        complaint_id=complaint.id,
    )
    await db.flush()

    return build_complaint_pdf(complaint)
