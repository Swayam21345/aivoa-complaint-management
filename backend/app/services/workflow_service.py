from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional, Set
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_event import AuditEvent
from app.models.complaint import Complaint

# ─── Allowed Status State Machine Transitions ─────────────────────────────────

ALLOWED_TRANSITIONS: Dict[str, Set[str]] = {
    "Draft": {"NEW", "TRIAGED", "UNDER_REVIEW", "IN_PROGRESS", "RESOLVED", "REJECTED"},
    "NEW": {"TRIAGED", "UNDER_REVIEW", "IN_PROGRESS", "RESOLVED", "REJECTED", "CANCELLED"},
    "TRIAGED": {"ASSIGNED", "UNDER_INVESTIGATION", "REJECTED", "CANCELLED", "ON_HOLD", "IN_PROGRESS", "RESOLVED"},
    "ASSIGNED": {"UNDER_INVESTIGATION", "ON_HOLD", "CANCELLED", "IN_PROGRESS", "RESOLVED"},
    "UNDER_INVESTIGATION": {"ROOT_CAUSE_IDENTIFIED", "CAPA_IN_PROGRESS", "QA_REVIEW", "RESOLVED", "CLOSED", "ON_HOLD", "CANCELLED"},
    "ROOT_CAUSE_IDENTIFIED": {"CAPA_IN_PROGRESS", "QA_REVIEW", "RESOLVED", "CLOSED", "ON_HOLD", "CANCELLED"},
    "CAPA_IN_PROGRESS": {"QA_REVIEW", "QA_APPROVED", "RESOLVED", "CLOSED", "ON_HOLD", "CANCELLED"},
    "QA_REVIEW": {"QA_APPROVED", "UNDER_INVESTIGATION", "RESOLVED", "CLOSED", "REJECTED", "CANCELLED", "ON_HOLD"},
    "QA_APPROVED": {"CLOSED", "RESOLVED"},
    "ON_HOLD": {"ASSIGNED", "UNDER_INVESTIGATION", "ROOT_CAUSE_IDENTIFIED", "CAPA_IN_PROGRESS", "QA_REVIEW", "IN_PROGRESS", "RESOLVED"},
    # Legacy compat states
    "UNDER_REVIEW": {"IN_PROGRESS", "TRIAGED", "ASSIGNED", "RESOLVED", "REJECTED", "CLOSED", "UNDER_INVESTIGATION"},
    "IN_PROGRESS": {"WAITING_CUSTOMER", "RESOLVED", "QA_REVIEW", "CLOSED", "REJECTED", "UNDER_INVESTIGATION", "ROOT_CAUSE_IDENTIFIED", "CAPA_IN_PROGRESS"},
    "WAITING_CUSTOMER": {"IN_PROGRESS", "RESOLVED", "CLOSED"},
    "RESOLVED": {"CLOSED", "IN_PROGRESS", "QA_APPROVED"},
    "Under Review": {"IN_PROGRESS", "RESOLVED", "CLOSED", "TRIAGED"},
    "Closed": set(),
    # Terminal states
    "CLOSED": set(),
    "REJECTED": set(),
    "CANCELLED": set(),
}

# ─── Role-Based Allowed Transitions ───────────────────────────────────────────

INVESTIGATOR_ALLOWED_TRANSITIONS: Set[tuple[str, str]] = {
    ("ASSIGNED", "UNDER_INVESTIGATION"),
    ("UNDER_INVESTIGATION", "ROOT_CAUSE_IDENTIFIED"),
    ("ROOT_CAUSE_IDENTIFIED", "CAPA_IN_PROGRESS"),
    ("CAPA_IN_PROGRESS", "QA_REVIEW"),
    ("UNDER_INVESTIGATION", "ON_HOLD"),
    ("CAPA_IN_PROGRESS", "ON_HOLD"),
    ("ON_HOLD", "UNDER_INVESTIGATION"),
    ("ON_HOLD", "CAPA_IN_PROGRESS"),
    # Legacy compat
    ("UNDER_REVIEW", "IN_PROGRESS"),
    ("IN_PROGRESS", "WAITING_CUSTOMER"),
    ("WAITING_CUSTOMER", "IN_PROGRESS"),
    ("IN_PROGRESS", "RESOLVED"),
    ("IN_PROGRESS", "QA_REVIEW"),
    ("RESOLVED", "CLOSED"),
}

QA_MANAGER_ALLOWED_TRANSITIONS: Set[tuple[str, str]] = {
    ("NEW", "TRIAGED"),
    ("NEW", "REJECTED"),
    ("NEW", "CANCELLED"),
    ("TRIAGED", "ASSIGNED"),
    ("TRIAGED", "UNDER_INVESTIGATION"),
    ("TRIAGED", "REJECTED"),
    ("TRIAGED", "CANCELLED"),
    ("TRIAGED", "ON_HOLD"),
    ("QA_REVIEW", "QA_APPROVED"),
    ("QA_REVIEW", "UNDER_INVESTIGATION"),
    ("QA_REVIEW", "REJECTED"),
    ("QA_REVIEW", "CANCELLED"),
    ("QA_APPROVED", "CLOSED"),
    ("ON_HOLD", "ASSIGNED"),
    ("ON_HOLD", "UNDER_INVESTIGATION"),
    ("ON_HOLD", "QA_REVIEW"),
    # Legacy compat
    ("Draft", "NEW"),
    ("NEW", "UNDER_REVIEW"),
    ("UNDER_REVIEW", "IN_PROGRESS"),
    ("IN_PROGRESS", "RESOLVED"),
    ("RESOLVED", "CLOSED"),
}


def validate_status_transition_for_role(user_role: str, old_status: str, new_status: str) -> None:
    """
    Enforces state machine rules AND role-based authorization for workflow transitions.
    Raises HTTP 400 Bad Request for state machine errors.
    Raises HTTP 403 Forbidden for unauthorized role attempts.
    """
    if old_status == new_status:
        return

    # 1. State machine transition check
    allowed_states = ALLOWED_TRANSITIONS.get(old_status, set())
    if new_status not in allowed_states:
        allowed_desc = ", ".join(sorted(allowed_states)) if allowed_states else "None (Terminal Status)"
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Invalid status transition from '{old_status}' to '{new_status}'. "
                f"Allowed next status(es) from '{old_status}': [{allowed_desc}]."
            ),
        )

    # 2. Role-based transition check
    if user_role == "ADMIN":
        return  # Admin has unrestricted authority

    if user_role == "VIEWER":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied: Viewer role has read-only access to workflow transitions.",
        )

    transition_pair = (old_status, new_status)

    if user_role == "INVESTIGATOR":
        if transition_pair not in INVESTIGATOR_ALLOWED_TRANSITIONS:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: Investigator role cannot transition complaint from '{old_status}' to '{new_status}'.",
            )
    elif user_role == "QA_MANAGER":
        # QA Manager can perform QA transitions plus investigator escalations
        if transition_pair not in QA_MANAGER_ALLOWED_TRANSITIONS and transition_pair not in INVESTIGATOR_ALLOWED_TRANSITIONS:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: QA Manager role cannot perform transition from '{old_status}' to '{new_status}'.",
            )


def calculate_sla_target_hours(priority: Optional[str], risk_level: Optional[str]) -> float:
    if priority == "Critical":
        return 24.0
    elif priority == "High" or risk_level == "High":
        return 72.0
    return 168.0  # 7 days


def evaluate_complaint_sla(complaint: Complaint) -> Dict[str, Any]:
    """
    Calculates SLA age metrics and evaluates ON_TRACK, AT_RISK, BREACHED status.
    """
    now = datetime.now(timezone.utc)
    created_at = complaint.created_at
    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)

    age_hours = round((now - created_at).total_seconds() / 3600.0, 2)
    sla_target_hours = calculate_sla_target_hours(complaint.priority, complaint.risk_level)

    # Calculate due date
    if complaint.due_date is None:
        due_date = created_at + timedelta(hours=sla_target_hours)
    else:
        due_date = complaint.due_date
        if due_date.tzinfo is None:
            due_date = due_date.replace(tzinfo=timezone.utc)

    remaining_hours = round((due_date - now).total_seconds() / 3600.0, 2)
    is_terminal = complaint.status in ("CLOSED", "RESOLVED", "REJECTED", "CANCELLED")

    if is_terminal:
        sla_status_str = "ON_TRACK"
        hours_until_due = max(0.0, remaining_hours)
        is_overdue = False
        near_sla = False
    elif remaining_hours <= 0:
        sla_status_str = "BREACHED"
        hours_until_due = 0.0
        is_overdue = True
        near_sla = False
    elif remaining_hours <= (sla_target_hours * 0.2):
        sla_status_str = "AT_RISK"
        hours_until_due = remaining_hours
        is_overdue = False
        near_sla = True
    else:
        sla_status_str = "ON_TRACK"
        hours_until_due = remaining_hours
        is_overdue = False
        near_sla = False

    # Auto escalate if breached or critical
    if not is_terminal and (is_overdue or complaint.is_escalated):
        if not complaint.is_escalated:
            complaint.is_escalated = True
            complaint.escalated_at = now
            complaint.escalation_reason = f"SLA threshold breached ({age_hours:.1f} hrs elapsed)."

    return {
        "created_at": created_at,
        "due_date": due_date,
        "sla_status": sla_status_str,
        "remaining_hours": remaining_hours,
        "age_hours": age_hours,
        "time_under_review_hours": age_hours,
        "sla_target_hours": sla_target_hours,
        "hours_until_due": hours_until_due,
        "is_overdue": is_overdue,
        "near_sla": near_sla,
        "is_escalated": complaint.is_escalated,
        "escalation_reason": complaint.escalation_reason,
        "escalated_at": complaint.escalated_at,
    }


async def log_audit_event(
    db: AsyncSession,
    action_type: str,
    description: str,
    actor_email: str = "system@aiccms.local",
    complaint_id: Optional[UUID] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> AuditEvent:
    """
    Creates an immutable audit event for regulatory tracking.
    """
    event = AuditEvent(
        complaint_id=complaint_id,
        actor_email=actor_email,
        action_type=action_type,
        description=description,
        event_metadata=metadata,
    )
    db.add(event)
    return event
