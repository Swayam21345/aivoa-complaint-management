import hashlib
import uuid
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import verify_password
from app.models.complaint import Complaint
from app.models.complaint_history import ComplaintHistory
from app.models.electronic_signature import ElectronicSignature
from app.models.user import User
from app.schemas.electronic_signature import (
    ElectronicSignatureCreate,
    ElectronicSignatureRead,
    ElectronicSignatureResponse,
)
from app.services.workflow_service import (
    ALLOWED_TRANSITIONS,
    log_audit_event,
    validate_status_transition_for_role,
)

# States that mandate an electronic signature before transition
SIGNATURE_REQUIRED_STATES = {"QA_APPROVED", "CLOSED"}

# Actions that sign a QMS entity without requiring a linked complaint record
ENTITY_SIGNATURE_ACTIONS = frozenset(
    {
        "RCA Approval",
        "Document Approval",
        "CAPA Closure",
        "CAPA Effectiveness Review",
        "Internal Audit Final Signoff",
        "Supplier Qualification Approval",
        "Document Acknowledgement",
    }
)


def hash_signature(
    complaint_id: uuid.UUID,
    user_id: uuid.UUID,
    timestamp: str,
    status_before: str,
    status_after: str,
    reason: str,
) -> str:
    """
    Generate a SHA-256 cryptographic checksum for the signature payload.

    Input: complaint_id:user_id:timestamp:status_before:status_after:reason
    Returns: 64-character hex digest
    """
    raw = f"{complaint_id}:{user_id}:{timestamp}:{status_before}:{status_after}:{reason}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def verify_signature_hash(
    signature: ElectronicSignature,
    complaint_id: uuid.UUID,
    user_id: uuid.UUID,
) -> bool:
    """
    Verify an existing signature record's hash has not been tampered with.
    Returns True if hash is valid, False otherwise.
    """
    timestamp_str = signature.signature_timestamp.isoformat()
    expected = hash_signature(
        complaint_id=complaint_id,
        user_id=user_id,
        timestamp=timestamp_str,
        status_before=signature.status_before,
        status_after=signature.status_after,
        reason=signature.reason,
    )
    return expected == signature.signature_hash


async def create_signature(
    db: AsyncSession,
    complaint_id: uuid.UUID | None,
    payload: ElectronicSignatureCreate,
    current_user: User,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> ElectronicSignatureResponse:
    """
    Executes 21 CFR Part 11 compliant electronic signature on a complaint.

    Steps:
    1. Verifies current user role permission (ADMIN or QA_MANAGER required).
    2. Re-authenticates user password.
    3. Retrieves the complaint.
    4. Validates workflow status transition.
    5. Computes SHA-256 cryptographic signature checksum.
    6. Saves immutable ElectronicSignature record.
    7. Updates complaint status & logs ComplaintHistory.
    8. Creates immutable AuditEvent.
    """
    # 1. Role Authorization
    if current_user.role not in ("ADMIN", "QA_MANAGER"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied: Only ADMIN and QA_MANAGER roles may execute electronic signatures.",
        )

    # 2. Password Re-authentication
    if not verify_password(payload.password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Electronic Signature failed: Password verification failed.",
        )

    is_entity_action = payload.action in ENTITY_SIGNATURE_ACTIONS or (
        (payload.action or "").startswith("CAPA Effectiveness Review")
    )

    # 3. Retrieve Complaint (optional for entity-level signatures)
    complaint: Complaint | None = None
    if complaint_id is not None:
        stmt = select(Complaint).where(
            Complaint.id == complaint_id,
            Complaint.is_deleted == False,  # noqa: E712
        )
        res = await db.execute(stmt)
        complaint = res.scalar_one_or_none()

    if complaint is None and not is_entity_action:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Complaint with ID '{complaint_id}' not found.",
        )

    status_before = complaint.status if complaint else "N/A"

    # 4. Determine Target Status
    if payload.target_status:
        target_status = payload.target_status
    elif status_before in ("QA_REVIEW",):
        target_status = "QA_APPROVED"
    elif status_before in ("QA_APPROVED",):
        target_status = "CLOSED"
    else:
        target_status = "QA_APPROVED"

    if not is_entity_action:
        # Validate state machine transition for complaint
        validate_status_transition_for_role(current_user.role, status_before, target_status)

        # Requirement: Complaint cannot move to QA_APPROVED unless all linked CAPAs are CLOSED
        if target_status == "QA_APPROVED" and complaint is not None:
            from app.services.capa_service import CAPAService
            are_closed = await CAPAService.are_all_complaint_capas_closed(db, complaint.id)
            if not are_closed:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot approve complaint: All associated CAPAs must be CLOSED before QA Approval.",
                )

    now = datetime.now(timezone.utc)
    now_iso = now.isoformat()

    # 5. Compute SHA-256 Hash
    hash_complaint_id = complaint.id if complaint else (complaint_id or uuid.UUID(int=0))
    sig_hash = hash_signature(
        complaint_id=hash_complaint_id,
        user_id=current_user.id,
        timestamp=now_iso,
        status_before=status_before,
        status_after=target_status,
        reason=payload.reason,
    )

    # 6. Create Signature Record
    action_name = payload.action or (
        "QA Approval" if target_status == "QA_APPROVED"
        else "Complaint Closure" if target_status == "CLOSED"
        else f"Electronic Signature ({target_status})"
    )

    sig_id = uuid.uuid4()
    sig_record = ElectronicSignature(
        id=sig_id,
        complaint_id=complaint.id if complaint else None,
        user_id=current_user.id,
        action=action_name,
        status_before=status_before,
        status_after=target_status,
        reason=payload.reason,
        signature_timestamp=now,
        ip_address=ip_address,
        user_agent=user_agent,
        signature_hash=sig_hash,
        created_at=now,
    )
    db.add(sig_record)

    # 7. Update Complaint Status & History if complaint transition action
    if not is_entity_action and complaint is not None:
        complaint.status = target_status
        complaint.updated_at = now

        history_entry = ComplaintHistory(
            complaint_id=complaint.id,
            old_status=status_before,
            new_status=target_status,
            changed_by=current_user.full_name or current_user.email,
            change_reason=f"Electronic Signature: {payload.reason}",
        )
        db.add(history_entry)

    # 8. Immutable Audit Event
    await log_audit_event(
        db,
        action_type="Electronic Signature",
        description=(
            f"21 CFR Part 11 Electronic Signature by {current_user.full_name} "
            f"({current_user.email}) for '{action_name}'. Rationale: {payload.reason}"
        ),
        actor_email=current_user.email,
        complaint_id=complaint.id if complaint else None,
        metadata={
            "signature_id": str(sig_id),
            "signature_hash": sig_hash,
            "status_before": status_before,
            "status_after": target_status,
            "reason": payload.reason,
        },
    )

    await db.flush()

    return ElectronicSignatureResponse(
        signed=True,
        signed_by=current_user.full_name or current_user.email,
        timestamp=now,
        signature_id=sig_id,
        hash=sig_hash,
    )



async def get_signature_history(
    db: AsyncSession,
    complaint_id: uuid.UUID,
) -> list[ElectronicSignatureRead]:
    """
    Returns all immutable electronic signature records for a complaint, newest first.
    """
    stmt = (
        select(ElectronicSignature, User.full_name)
        .join(User, ElectronicSignature.user_id == User.id)
        .where(ElectronicSignature.complaint_id == complaint_id)
        .order_by(ElectronicSignature.signature_timestamp.desc())
    )
    result = await db.execute(stmt)
    rows = result.all()

    output: list[ElectronicSignatureRead] = []
    for sig, full_name in rows:
        sig_read = ElectronicSignatureRead.model_validate(sig)
        sig_read.user_name = full_name
        output.append(sig_read)

    return output
