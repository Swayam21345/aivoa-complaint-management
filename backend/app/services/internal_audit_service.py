from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.internal_audit import (
    AuditChecklist,
    AuditFinding,
    InspectionReadinessPackage,
    InternalAudit,
)
from app.models.user import User
from app.schemas.electronic_signature import ElectronicSignatureCreate
from app.schemas.internal_audit import (
    AuditApprovalCreate,
    AuditChecklistCreate,
    AuditFindingCreate,
    InspectionReadinessCreate,
    InternalAuditCreate,
    InternalAuditUpdate,
)
from app.services.signature_service import create_signature
from app.services.workflow_service import log_audit_event


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


async def generate_audit_number(db: AsyncSession) -> str:
    year = datetime.now().year
    prefix = f"IAU-{year}-"
    stmt = (
        select(InternalAudit.audit_number)
        .where(InternalAudit.audit_number.like(f"{prefix}%"))
        .order_by(InternalAudit.audit_number.desc())
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


async def generate_finding_number(db: AsyncSession) -> str:
    year = datetime.now().year
    prefix = f"AFN-{year}-"
    stmt = (
        select(AuditFinding.finding_number)
        .where(AuditFinding.finding_number.like(f"{prefix}%"))
        .order_by(AuditFinding.finding_number.desc())
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


async def generate_package_number(db: AsyncSession) -> str:
    year = datetime.now().year
    prefix = f"IRP-{year}-"
    stmt = (
        select(InspectionReadinessPackage.package_number)
        .where(InspectionReadinessPackage.package_number.like(f"{prefix}%"))
        .order_by(InspectionReadinessPackage.package_number.desc())
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


# ─── Internal Audit CRUD ──────────────────────────────────────────────────────
async def create_internal_audit(
    db: AsyncSession, payload: InternalAuditCreate, current_user: User
) -> InternalAudit:
    num = await generate_audit_number(db)
    creator_name = current_user.full_name or current_user.email

    audit = InternalAudit(
        audit_number=num,
        title=payload.title,
        audit_type=payload.audit_type,
        scope=payload.scope,
        lead_auditor=payload.lead_auditor,
        audit_team=payload.audit_team,
        department=payload.department,
        scheduled_start_date=payload.scheduled_start_date,
        scheduled_end_date=payload.scheduled_end_date,
        status="PLANNED",
        created_by=creator_name,
        updated_by=creator_name,
    )
    db.add(audit)
    await db.flush()

    await log_audit_event(
        db,
        action_type="Internal Audit Planned",
        description=f"Internal Audit '{audit.audit_number}: {audit.title}' created by {current_user.email}",
        actor_email=current_user.email,
        metadata={"audit_id": str(audit.id), "audit_number": audit.audit_number},
    )
    await db.commit()
    return await get_internal_audit_detail(db, audit.id)


async def list_internal_audits(
    db: AsyncSession,
    status_filter: Optional[str] = None,
    department: Optional[str] = None,
    search: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
) -> Tuple[List[InternalAudit], int]:
    stmt = select(InternalAudit)
    if status_filter:
        stmt = stmt.where(InternalAudit.status == status_filter)
    if department:
        stmt = stmt.where(InternalAudit.department == department)
    if search:
        pattern = f"%{search}%"
        stmt = stmt.where(
            (InternalAudit.title.ilike(pattern))
            | (InternalAudit.audit_number.ilike(pattern))
            | (InternalAudit.lead_auditor.ilike(pattern))
        )

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = (await db.execute(count_stmt)).scalar_one()

    stmt = stmt.order_by(InternalAudit.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    audits = list((await db.execute(stmt)).scalars().all())

    for a in audits:
        a.checklists = list((await db.execute(select(AuditChecklist).where(AuditChecklist.audit_id == a.id))).scalars().all())
        a.findings = list((await db.execute(select(AuditFinding).where(AuditFinding.audit_id == a.id))).scalars().all())

    return audits, total


async def get_internal_audit_detail(db: AsyncSession, audit_id: UUID) -> InternalAudit:
    stmt = select(InternalAudit).where(InternalAudit.id == audit_id)
    res = await db.execute(stmt)
    audit = res.scalar_one_or_none()

    if not audit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Internal audit record not found"
        )

    audit.checklists = list((await db.execute(select(AuditChecklist).where(AuditChecklist.audit_id == audit.id))).scalars().all())
    audit.findings = list((await db.execute(select(AuditFinding).where(AuditFinding.audit_id == audit.id))).scalars().all())

    return audit


async def update_internal_audit(
    db: AsyncSession, audit_id: UUID, payload: InternalAuditUpdate, current_user: User
) -> InternalAudit:
    audit = await get_internal_audit_detail(db, audit_id)

    if payload.title is not None:
        audit.title = payload.title
    if payload.audit_type is not None:
        audit.audit_type = payload.audit_type
    if payload.scope is not None:
        audit.scope = payload.scope
    if payload.lead_auditor is not None:
        audit.lead_auditor = payload.lead_auditor
    if payload.audit_team is not None:
        audit.audit_team = payload.audit_team
    if payload.department is not None:
        audit.department = payload.department
    if payload.scheduled_start_date is not None:
        audit.scheduled_start_date = payload.scheduled_start_date
    if payload.scheduled_end_date is not None:
        audit.scheduled_end_date = payload.scheduled_end_date
    if payload.actual_start_date is not None:
        audit.actual_start_date = payload.actual_start_date
    if payload.actual_end_date is not None:
        audit.actual_end_date = payload.actual_end_date
    if payload.status is not None:
        audit.status = payload.status
    if payload.conclusion is not None:
        audit.conclusion = payload.conclusion

    audit.updated_by = current_user.full_name or current_user.email
    audit.updated_at = now_utc()

    await db.flush()

    await log_audit_event(
        db,
        action_type="Internal Audit Updated",
        description=f"Audit '{audit.audit_number}' updated by {current_user.email}",
        actor_email=current_user.email,
        metadata={"audit_id": str(audit.id)},
    )
    await db.commit()
    return await get_internal_audit_detail(db, audit_id)


# ─── Checklist & Findings ─────────────────────────────────────────────────────
async def add_audit_checklist_item(
    db: AsyncSession, audit_id: UUID, payload: AuditChecklistCreate, current_user: User
) -> AuditChecklist:
    audit = await get_internal_audit_detail(db, audit_id)

    chk = AuditChecklist(
        audit_id=audit.id,
        section=payload.section,
        requirement=payload.requirement,
        question=payload.question,
        compliance_status=payload.compliance_status,
        comments=payload.comments,
        evidence_summary=payload.evidence_summary,
    )
    db.add(chk)
    await db.flush()

    await log_audit_event(
        db,
        action_type="Audit Checklist Item Added",
        description=f"Checklist item added to audit {audit.audit_number} by {current_user.email}",
        actor_email=current_user.email,
        metadata={"checklist_id": str(chk.id)},
    )
    await db.commit()
    return chk


async def add_audit_finding(
    db: AsyncSession, audit_id: UUID, payload: AuditFindingCreate, current_user: User
) -> AuditFinding:
    audit = await get_internal_audit_detail(db, audit_id)
    finding_num = await generate_finding_number(db)

    finding = AuditFinding(
        audit_id=audit.id,
        finding_number=finding_num,
        category=payload.category,
        description=payload.description,
        clause_reference=payload.clause_reference,
        capa_id=payload.capa_id,
        status="OPEN" if not payload.capa_id else "CAPA_ASSIGNED",
    )
    db.add(finding)
    await db.flush()

    await log_audit_event(
        db,
        action_type="Audit Finding Logged",
        description=f"Finding '{finding.finding_number}' ({finding.category}) logged for audit {audit.audit_number}",
        actor_email=current_user.email,
        metadata={"finding_id": str(finding.id), "category": finding.category},
    )
    await db.commit()
    return finding


# ─── Audit Approval Workflow (21 CFR Part 11) ──────────────────────────────────
async def approve_and_close_audit(
    db: AsyncSession, audit_id: UUID, payload: AuditApprovalCreate, current_user: User
) -> InternalAudit:
    audit = await get_internal_audit_detail(db, audit_id)
    if audit.status == "CLOSED":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Audit {audit.audit_number} is already CLOSED.",
        )

    # Re-authenticate & Signature verification
    sig_res = await create_signature(
        db=db,
        complaint_id=None,
        payload=ElectronicSignatureCreate(
            password=payload.password,
            reason=payload.reason,
            action="Internal Audit Final Signoff",
            target_status="CLOSED",
        ),
        current_user=current_user,
    )

    now = now_utc()
    audit.status = "CLOSED"
    if payload.conclusion:
        audit.conclusion = payload.conclusion
    audit.approved_by = current_user.full_name or current_user.email
    audit.approved_at = now
    audit.actual_end_date = now if not audit.actual_end_date else audit.actual_end_date
    audit.updated_by = current_user.full_name or current_user.email
    audit.updated_at = now

    await log_audit_event(
        db,
        action_type="Internal Audit Closed",
        description=f"Approved & closed internal audit {audit.audit_number} with 21 CFR Part 11 e-signature",
        actor_email=current_user.email,
        metadata={"audit_id": str(audit.id), "signature_id": str(sig_res.signature_id)},
    )
    await db.commit()
    return await get_internal_audit_detail(db, audit_id)


# ─── Inspection Readiness Packages ───────────────────────────────────────────
async def create_inspection_readiness_package(
    db: AsyncSession, payload: InspectionReadinessCreate, current_user: User
) -> InspectionReadinessPackage:
    num = await generate_package_number(db)
    creator_name = current_user.full_name or current_user.email

    pkg = InspectionReadinessPackage(
        package_number=num,
        agency=payload.agency,
        title=payload.title,
        description=payload.description,
        readiness_score=payload.readiness_score,
        status="READY",
        created_by=creator_name,
        updated_by=creator_name,
    )
    db.add(pkg)
    await db.flush()

    await log_audit_event(
        db,
        action_type="Inspection Readiness Package Created",
        description=f"Inspection Readiness Package '{pkg.package_number}' ({pkg.agency}) created by {current_user.email}",
        actor_email=current_user.email,
        metadata={"package_id": str(pkg.id)},
    )
    await db.commit()
    return pkg


async def list_inspection_readiness_packages(db: AsyncSession) -> List[InspectionReadinessPackage]:
    stmt = select(InspectionReadinessPackage).order_by(InspectionReadinessPackage.created_at.desc())
    return list((await db.execute(stmt)).scalars().all())


# ─── Dashboard Metrics ────────────────────────────────────────────────────────
async def get_internal_audit_dashboard_metrics(db: AsyncSession) -> Dict[str, Any]:
    res = await db.execute(select(InternalAudit))
    audits = list(res.scalars().all())

    total = len(audits)
    planned = len([a for a in audits if a.status == "PLANNED"])
    in_progress = len([a for a in audits if a.status == "IN_PROGRESS"])
    closed = len([a for a in audits if a.status == "CLOSED"])

    find_res = await db.execute(select(AuditFinding))
    findings = list(find_res.scalars().all())
    total_findings = len(findings)
    critical_findings = len([f for f in findings if f.category == "CRITICAL_NC"])
    open_findings = len([f for f in findings if f.status in ("OPEN", "CAPA_ASSIGNED")])

    pkg_res = await db.execute(select(InspectionReadinessPackage.readiness_score))
    scores = [s for s in pkg_res.scalars().all() if s is not None]
    avg_score = round(sum(scores) / len(scores), 1) if scores else 100.0

    by_dept: Dict[str, int] = {}
    for a in audits:
        by_dept[a.department] = by_dept.get(a.department, 0) + 1

    by_cat: Dict[str, int] = {}
    for f in findings:
        by_cat[f.category] = by_cat.get(f.category, 0) + 1

    return {
        "total_audits": total,
        "planned_audits": planned,
        "in_progress_audits": in_progress,
        "closed_audits": closed,
        "total_findings": total_findings,
        "critical_findings_count": critical_findings,
        "open_findings_count": open_findings,
        "avg_inspection_readiness_score": avg_score,
        "by_department": by_dept,
        "by_category": by_cat,
    }
