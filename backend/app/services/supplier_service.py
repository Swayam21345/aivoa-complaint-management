from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple, Any
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.supplier import (
    Supplier,
    SupplierAudit,
    SupplierContact,
    SupplierCorrectiveAction,
    SupplierDocument,
    SupplierNonconformance,
    SupplierScorecard,
)
from app.models.user import User
from app.schemas.electronic_signature import ElectronicSignatureCreate
from app.schemas.supplier import (
    SupplierApprovalCreate,
    SupplierAuditCreate,
    SupplierContactCreate,
    SupplierCorrectiveActionCreate,
    SupplierCreate,
    SupplierNonconformanceCreate,
    SupplierScorecardCreate,
    SupplierUpdate,
)
from app.services.signature_service import create_signature
from app.services.workflow_service import log_audit_event


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


async def generate_supplier_number(db: AsyncSession) -> str:
    year = datetime.now().year
    prefix = f"SUP-{year}-"
    stmt = (
        select(Supplier.supplier_number)
        .where(Supplier.supplier_number.like(f"{prefix}%"))
        .order_by(Supplier.supplier_number.desc())
        .limit(1)
    )
    res = await db.execute(stmt)
    last_num = res.scalar_one_or_none()

    if not last_num:
        seq = 1
    else:
        try:
            seq = int(last_num.split("-")[-1]) + 1
        except ValueError:
            seq = 1
    return f"{prefix}{seq:04d}"


async def generate_audit_number(db: AsyncSession) -> str:
    year = datetime.now().year
    prefix = f"AUD-{year}-"
    stmt = (
        select(SupplierAudit.audit_number)
        .where(SupplierAudit.audit_number.like(f"{prefix}%"))
        .order_by(SupplierAudit.audit_number.desc())
        .limit(1)
    )
    res = await db.execute(stmt)
    last_num = res.scalar_one_or_none()

    if not last_num:
        seq = 1
    else:
        try:
            seq = int(last_num.split("-")[-1]) + 1
        except ValueError:
            seq = 1
    return f"{prefix}{seq:04d}"


async def generate_ncr_number(db: AsyncSession) -> str:
    year = datetime.now().year
    prefix = f"NCR-{year}-"
    stmt = (
        select(SupplierNonconformance.ncr_number)
        .where(SupplierNonconformance.ncr_number.like(f"{prefix}%"))
        .order_by(SupplierNonconformance.ncr_number.desc())
        .limit(1)
    )
    res = await db.execute(stmt)
    last_num = res.scalar_one_or_none()

    if not last_num:
        seq = 1
    else:
        try:
            seq = int(last_num.split("-")[-1]) + 1
        except ValueError:
            seq = 1
    return f"{prefix}{seq:04d}"


async def generate_sca_number(db: AsyncSession) -> str:
    year = datetime.now().year
    prefix = f"SCA-{year}-"
    stmt = (
        select(SupplierCorrectiveAction.action_number)
        .where(SupplierCorrectiveAction.action_number.like(f"{prefix}%"))
        .order_by(SupplierCorrectiveAction.action_number.desc())
        .limit(1)
    )
    res = await db.execute(stmt)
    last_num = res.scalar_one_or_none()

    if not last_num:
        seq = 1
    else:
        try:
            seq = int(last_num.split("-")[-1]) + 1
        except ValueError:
            seq = 1
    return f"{prefix}{seq:04d}"


# ─── Supplier CRUD ────────────────────────────────────────────────────────────
async def create_supplier(
    db: AsyncSession, payload: SupplierCreate, current_user: User
) -> Supplier:
    sup_num = await generate_supplier_number(db)
    creator_name = current_user.full_name or current_user.email

    supplier = Supplier(
        supplier_number=sup_num,
        supplier_name=payload.supplier_name,
        supplier_type=payload.supplier_type,
        category=payload.category,
        status="PENDING_QUALIFICATION",
        risk_level=payload.risk_level,
        address=payload.address,
        city=payload.city,
        state=payload.state,
        country=payload.country,
        zip_code=payload.zip_code,
        phone=payload.phone,
        email=payload.email,
        website=payload.website,
        approval_status="PENDING",
        created_by=creator_name,
        updated_by=creator_name,
    )
    db.add(supplier)
    await db.flush()

    await log_audit_event(
        db,
        action_type="Supplier Created",
        description=f"Supplier '{supplier.supplier_number}: {supplier.supplier_name}' created by {current_user.email}",
        actor_email=current_user.email,
        metadata={"supplier_id": str(supplier.id), "supplier_number": supplier.supplier_number},
    )
    await db.commit()
    return await get_supplier_detail(db, supplier.id)


async def list_suppliers(
    db: AsyncSession,
    status_filter: Optional[str] = None,
    risk_level: Optional[str] = None,
    supplier_type: Optional[str] = None,
    search: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
) -> Tuple[List[Supplier], int]:
    stmt = select(Supplier)
    if status_filter:
        stmt = stmt.where(Supplier.status == status_filter)
    if risk_level:
        stmt = stmt.where(Supplier.risk_level == risk_level)
    if supplier_type:
        stmt = stmt.where(Supplier.supplier_type == supplier_type)
    if search:
        pattern = f"%{search}%"
        stmt = stmt.where(
            (Supplier.supplier_name.ilike(pattern))
            | (Supplier.supplier_number.ilike(pattern))
            | (Supplier.email.ilike(pattern))
        )

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = (await db.execute(count_stmt)).scalar_one()

    stmt = stmt.order_by(Supplier.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    suppliers = list((await db.execute(stmt)).scalars().all())

    # Populate sub-entities manually for response
    for s in suppliers:
        s.contacts = list((await db.execute(select(SupplierContact).where(SupplierContact.supplier_id == s.id))).scalars().all())
        s.audits = list((await db.execute(select(SupplierAudit).where(SupplierAudit.supplier_id == s.id))).scalars().all())
        s.scorecards = list((await db.execute(select(SupplierScorecard).where(SupplierScorecard.supplier_id == s.id))).scalars().all())
        s.nonconformances = list((await db.execute(select(SupplierNonconformance).where(SupplierNonconformance.supplier_id == s.id))).scalars().all())
        s.corrective_actions = list((await db.execute(select(SupplierCorrectiveAction).where(SupplierCorrectiveAction.supplier_id == s.id))).scalars().all())

    return suppliers, total


async def get_supplier_detail(db: AsyncSession, supplier_id: UUID) -> Supplier:
    stmt = select(Supplier).where(Supplier.id == supplier_id)
    res = await db.execute(stmt)
    supplier = res.scalar_one_or_none()

    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Supplier record not found"
        )

    supplier.contacts = list((await db.execute(select(SupplierContact).where(SupplierContact.supplier_id == supplier.id))).scalars().all())
    supplier.audits = list((await db.execute(select(SupplierAudit).where(SupplierAudit.supplier_id == supplier.id))).scalars().all())
    supplier.scorecards = list((await db.execute(select(SupplierScorecard).where(SupplierScorecard.supplier_id == supplier.id))).scalars().all())
    supplier.nonconformances = list((await db.execute(select(SupplierNonconformance).where(SupplierNonconformance.supplier_id == supplier.id))).scalars().all())
    supplier.corrective_actions = list((await db.execute(select(SupplierCorrectiveAction).where(SupplierCorrectiveAction.supplier_id == supplier.id))).scalars().all())

    return supplier


async def update_supplier(
    db: AsyncSession, supplier_id: UUID, payload: SupplierUpdate, current_user: User
) -> Supplier:
    supplier = await get_supplier_detail(db, supplier_id)

    if payload.supplier_name is not None:
        supplier.supplier_name = payload.supplier_name
    if payload.supplier_type is not None:
        supplier.supplier_type = payload.supplier_type
    if payload.category is not None:
        supplier.category = payload.category
    if payload.status is not None:
        supplier.status = payload.status
    if payload.risk_level is not None:
        supplier.risk_level = payload.risk_level
    if payload.address is not None:
        supplier.address = payload.address
    if payload.city is not None:
        supplier.city = payload.city
    if payload.state is not None:
        supplier.state = payload.state
    if payload.country is not None:
        supplier.country = payload.country
    if payload.zip_code is not None:
        supplier.zip_code = payload.zip_code
    if payload.phone is not None:
        supplier.phone = payload.phone
    if payload.email is not None:
        supplier.email = payload.email
    if payload.website is not None:
        supplier.website = payload.website

    supplier.updated_by = current_user.full_name or current_user.email
    supplier.updated_at = now_utc()

    await db.flush()

    await log_audit_event(
        db,
        action_type="Supplier Updated",
        description=f"Supplier '{supplier.supplier_number}' updated by {current_user.email}",
        actor_email=current_user.email,
        metadata={"supplier_id": str(supplier.id)},
    )
    await db.commit()
    return await get_supplier_detail(db, supplier_id)


async def delete_supplier(db: AsyncSession, supplier_id: UUID, current_user: User) -> None:
    supplier = await get_supplier_detail(db, supplier_id)
    await db.delete(supplier)

    await log_audit_event(
        db,
        action_type="Supplier Deleted",
        description=f"Supplier '{supplier.supplier_number}' deleted by {current_user.email}",
        actor_email=current_user.email,
        metadata={"supplier_id": str(supplier_id)},
    )
    await db.commit()


# ─── Approval Workflow (21 CFR Part 11) ──────────────────────────────────────
async def approve_supplier(
    db: AsyncSession, supplier_id: UUID, payload: SupplierApprovalCreate, current_user: User
) -> Supplier:
    supplier = await get_supplier_detail(db, supplier_id)
    if supplier.status == "APPROVED":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Supplier {supplier.supplier_number} is already APPROVED.",
        )

    # Electronic Signature Validation
    sig_res = await create_signature(
        db=db,
        complaint_id=None,
        payload=ElectronicSignatureCreate(
            password=payload.password,
            reason=payload.reason,
            action="Supplier Qualification Approval",
            target_status="APPROVED",
        ),
        current_user=current_user,
    )

    now = now_utc()
    supplier.status = "APPROVED"
    supplier.approval_status = "APPROVED"
    supplier.approved_by = current_user.full_name or current_user.email
    supplier.approved_at = now
    supplier.updated_by = current_user.full_name or current_user.email
    supplier.updated_at = now

    await log_audit_event(
        db,
        action_type="Supplier Approved",
        description=f"Approved supplier {supplier.supplier_number} with 21 CFR Part 11 e-signature by {current_user.email}",
        actor_email=current_user.email,
        metadata={"supplier_id": str(supplier.id), "signature_id": str(sig_res.signature_id)},
    )
    await db.commit()
    return await get_supplier_detail(db, supplier_id)


# ─── Audits & Scorecards ──────────────────────────────────────────────────────
async def schedule_supplier_audit(
    db: AsyncSession, supplier_id: UUID, payload: SupplierAuditCreate, current_user: User
) -> SupplierAudit:
    supplier = await get_supplier_detail(db, supplier_id)
    audit_num = await generate_audit_number(db)

    audit = SupplierAudit(
        supplier_id=supplier.id,
        audit_number=audit_num,
        audit_type=payload.audit_type,
        scheduled_date=payload.scheduled_date,
        auditor=payload.auditor,
        status="SCHEDULED",
        score=payload.score,
        findings_summary=payload.findings_summary,
    )
    db.add(audit)
    await db.flush()

    await log_audit_event(
        db,
        action_type="Supplier Audit Scheduled",
        description=f"Audit '{audit.audit_number}' scheduled for supplier {supplier.supplier_number} by {current_user.email}",
        actor_email=current_user.email,
        metadata={"audit_id": str(audit.id), "supplier_id": str(supplier.id)},
    )
    await db.commit()
    return audit


async def add_supplier_scorecard(
    db: AsyncSession, supplier_id: UUID, payload: SupplierScorecardCreate, current_user: User
) -> SupplierScorecard:
    supplier = await get_supplier_detail(db, supplier_id)
    overall = round((payload.quality_score * 0.4) + (payload.delivery_score * 0.3) + (payload.compliance_score * 0.3), 1)

    if overall >= 90:
        grade = "A"
    elif overall >= 80:
        grade = "B"
    elif overall >= 70:
        grade = "C"
    elif overall >= 60:
        grade = "D"
    else:
        grade = "F"

    scorecard = SupplierScorecard(
        supplier_id=supplier.id,
        period=payload.period,
        quality_score=payload.quality_score,
        delivery_score=payload.delivery_score,
        compliance_score=payload.compliance_score,
        overall_score=overall,
        grade=grade,
        evaluated_by=current_user.full_name or current_user.email,
        evaluated_at=now_utc(),
    )
    db.add(scorecard)
    await db.flush()

    await log_audit_event(
        db,
        action_type="Supplier Scorecard Added",
        description=f"Scorecard period '{payload.period}' (Overall: {overall}%, Grade: {grade}) logged for supplier {supplier.supplier_number}",
        actor_email=current_user.email,
        metadata={"scorecard_id": str(scorecard.id), "grade": grade},
    )
    await db.commit()
    return scorecard


async def add_supplier_nonconformance(
    db: AsyncSession, supplier_id: UUID, payload: SupplierNonconformanceCreate, current_user: User
) -> SupplierNonconformance:
    supplier = await get_supplier_detail(db, supplier_id)
    ncr_num = await generate_ncr_number(db)

    ncr = SupplierNonconformance(
        supplier_id=supplier.id,
        complaint_id=payload.complaint_id,
        ncr_number=ncr_num,
        title=payload.title,
        description=payload.description,
        severity=payload.severity,
        status="OPEN",
    )
    db.add(ncr)
    await db.flush()

    await log_audit_event(
        db,
        action_type="Supplier Nonconformance Logged",
        description=f"Nonconformance '{ncr.ncr_number}' logged for supplier {supplier.supplier_number}",
        actor_email=current_user.email,
        metadata={"ncr_id": str(ncr.id)},
    )
    await db.commit()
    return ncr


async def add_supplier_corrective_action(
    db: AsyncSession, supplier_id: UUID, payload: SupplierCorrectiveActionCreate, current_user: User
) -> SupplierCorrectiveAction:
    supplier = await get_supplier_detail(db, supplier_id)
    sca_num = await generate_sca_number(db)
    due_date = now_utc() + timedelta(days=payload.due_days)

    sca = SupplierCorrectiveAction(
        supplier_id=supplier.id,
        capa_id=payload.capa_id,
        action_number=sca_num,
        action_plan=payload.action_plan,
        owner=payload.owner,
        due_date=due_date,
        status="OPEN",
    )
    db.add(sca)
    await db.flush()

    await log_audit_event(
        db,
        action_type="Supplier CAPA Assigned",
        description=f"Supplier Corrective Action '{sca.action_number}' assigned for supplier {supplier.supplier_number}",
        actor_email=current_user.email,
        metadata={"sca_id": str(sca.id)},
    )
    await db.commit()
    return sca


# ─── Dashboard & Reports ──────────────────────────────────────────────────────
async def get_supplier_dashboard_metrics(db: AsyncSession) -> Dict[str, Any]:
    res = await db.execute(select(Supplier))
    suppliers = list(res.scalars().all())

    total = len(suppliers)
    approved = len([s for s in suppliers if s.status == "APPROVED"])
    pending = len([s for s in suppliers if s.status == "PENDING_QUALIFICATION"])
    disqualified = len([s for s in suppliers if s.status == "DISQUALIFIED"])

    risk_dist: Dict[str, int] = {}
    status_dist: Dict[str, int] = {}
    by_type: Dict[str, int] = {}

    for s in suppliers:
        risk_dist[s.risk_level] = risk_dist.get(s.risk_level, 0) + 1
        status_dist[s.status] = status_dist.get(s.status, 0) + 1
        by_type[s.supplier_type] = by_type.get(s.supplier_type, 0) + 1

    aud_res = await db.execute(select(func.count()).select_from(SupplierAudit).where(SupplierAudit.status == "SCHEDULED"))
    upcoming_audits = aud_res.scalar_one() or 0

    sca_res = await db.execute(select(func.count()).select_from(SupplierCorrectiveAction).where(SupplierCorrectiveAction.status == "OPEN"))
    open_scas = sca_res.scalar_one() or 0

    sc_res = await db.execute(select(SupplierScorecard.overall_score))
    scores = [s for s in sc_res.scalars().all() if s is not None]
    avg_score = round(sum(scores) / len(scores), 1) if scores else 100.0

    return {
        "total_suppliers": total,
        "approved_suppliers": approved,
        "pending_approvals": pending,
        "disqualified_suppliers": disqualified,
        "risk_distribution": risk_dist,
        "status_distribution": status_dist,
        "by_type": by_type,
        "upcoming_audits_count": upcoming_audits,
        "open_supplier_capas_count": open_scas,
        "avg_overall_score": avg_score,
    }
