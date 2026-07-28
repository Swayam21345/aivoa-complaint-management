import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.complaint import Complaint
from app.models.rca import FMEAAssessment, RCARecord
from app.models.user import User
from app.schemas.electronic_signature import ElectronicSignatureCreate
from app.schemas.rca import (
    FishboneCategories,
    FiveWhyItem,
    FMEAAssessmentCreate,
    FMEAAssessmentRead,
    RCAApproveRequest,
    RCACreate,
    RCADashboardRead,
    RCAListResponse,
    RCARead,
    RCAUpdate,
)
from app.services.signature_service import create_signature
from app.services.workflow_service import log_audit_event


def calculate_rpn(severity: int, occurrence: int, detection: int) -> Tuple[int, str]:
    """
    Calculates Risk Priority Number (RPN = Severity * Occurrence * Detection).
    Determines Risk Classification:
    - High: RPN >= 200 or Severity >= 8
    - Medium: RPN 100-199
    - Low: RPN 1-99
    """
    sev = max(1, min(10, severity))
    occ = max(1, min(10, occurrence))
    det = max(1, min(10, detection))

    rpn = sev * occ * det

    if rpn >= 200 or sev >= 8:
        risk_class = "High"
    elif rpn >= 100:
        risk_class = "Medium"
    else:
        risk_class = "Low"

    return rpn, risk_class


class RCAService:
    @staticmethod
    async def generate_rca_number(db: AsyncSession) -> str:
        year_str = datetime.now(timezone.utc).strftime("%Y")
        prefix = f"RCA-{year_str}-"
        stmt = select(func.count()).select_from(RCARecord).where(RCARecord.rca_number.like(f"{prefix}%"))
        count = (await db.execute(stmt)).scalar_one() or 0
        return f"{prefix}{count + 1:04d}"

    @staticmethod
    async def get_rca_or_404(db: AsyncSession, rca_id: UUID) -> RCARecord:
        stmt = select(RCARecord).where(RCARecord.id == rca_id)
        res = await db.execute(stmt)
        rca = res.scalar_one_or_none()
        if not rca:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"RCA investigation record '{rca_id}' not found.",
            )
        return rca

    @staticmethod
    async def create_rca(
        db: AsyncSession,
        payload: RCACreate,
        current_user: User,
    ) -> RCARead:
        comp_stmt = select(Complaint).where(Complaint.id == payload.complaint_id, Complaint.is_deleted == False)  # noqa: E712
        comp_res = await db.execute(comp_stmt)
        complaint = comp_res.scalar_one_or_none()
        if not complaint:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Parent complaint record '{payload.complaint_id}' not found.",
            )

        rca_number = await RCAService.generate_rca_number(db)
        creator_name = current_user.full_name or current_user.email

        whys_json = json.dumps([item.model_dump() for item in payload.five_whys]) if payload.five_whys else None
        fish_json = json.dumps(payload.fishbone.model_dump()) if payload.fishbone else None

        rca = RCARecord(
            complaint_id=payload.complaint_id,
            rca_number=rca_number,
            methodology=payload.methodology,
            primary_root_cause=payload.primary_root_cause,
            root_cause_category=payload.root_cause_category,
            five_whys_json=whys_json,
            fishbone_json=fish_json,
            contributing_factors=payload.contributing_factors,
            status="DRAFT",
            created_by=creator_name,
            updated_by=creator_name,
        )
        db.add(rca)
        await db.flush()

        # Add FMEA items if provided
        if payload.fmea_items:
            for item in payload.fmea_items:
                rpn, risk_class = calculate_rpn(item.severity, item.occurrence, item.detection)
                fmea = FMEAAssessment(
                    rca_id=rca.id,
                    complaint_id=complaint.id,
                    failure_mode=item.failure_mode,
                    effect_of_failure=item.effect_of_failure,
                    severity=item.severity,
                    occurrence=item.occurrence,
                    detection=item.detection,
                    rpn=rpn,
                    risk_class=risk_class,
                    recommended_action=item.recommended_action,
                    created_by=creator_name,
                    updated_by=creator_name,
                )
                db.add(fmea)

        await log_audit_event(
            db=db,
            action_type="RCA Created",
            description=f"Created Root Cause Investigation {rca_number} for Complaint {complaint.complaint_id}.",
            actor_email=current_user.email,
            complaint_id=complaint.id,
            metadata={"rca_id": str(rca.id), "rca_number": rca_number, "category": payload.root_cause_category},
        )

        await db.commit()
        await db.refresh(rca)
        return RCAService._to_read_schema(rca, complaint_number=complaint.complaint_id)

    @staticmethod
    async def get_rca_detail(db: AsyncSession, rca_id: UUID) -> RCARead:
        rca = await RCAService.get_rca_or_404(db, rca_id)
        comp_number = rca.complaint.complaint_id if rca.complaint else None
        return RCAService._to_read_schema(rca, complaint_number=comp_number)

    @staticmethod
    async def update_rca(
        db: AsyncSession,
        rca_id: UUID,
        payload: RCAUpdate,
        current_user: User,
    ) -> RCARead:
        rca = await RCAService.get_rca_or_404(db, rca_id)
        updater_name = current_user.full_name or current_user.email

        if payload.primary_root_cause is not None:
            rca.primary_root_cause = payload.primary_root_cause
        if payload.root_cause_category is not None:
            rca.root_cause_category = payload.root_cause_category
        if payload.methodology is not None:
            rca.methodology = payload.methodology
        if payload.five_whys is not None:
            rca.five_whys_json = json.dumps([item.model_dump() for item in payload.five_whys])
        if payload.fishbone is not None:
            rca.fishbone_json = json.dumps(payload.fishbone.model_dump())
        if payload.contributing_factors is not None:
            rca.contributing_factors = payload.contributing_factors
        if payload.status is not None and payload.status != rca.status:
            if payload.status == "APPROVED":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="RCA approval requires 21 CFR Part 11 electronic signature via POST /api/rca/{id}/approve.",
                )
            old_s = rca.status
            rca.status = payload.status
            await log_audit_event(
                db=db,
                action_type="RCA Status Updated",
                description=f"Updated RCA {rca.rca_number} status from {old_s} to {payload.status}.",
                actor_email=current_user.email,
                complaint_id=rca.complaint_id,
            )

        rca.updated_by = updater_name
        rca.updated_at = datetime.now(timezone.utc)

        await db.commit()
        await db.refresh(rca)
        comp_number = rca.complaint.complaint_id if rca.complaint else None
        return RCAService._to_read_schema(rca, complaint_number=comp_number)

    @staticmethod
    async def approve_rca(
        db: AsyncSession,
        rca_id: UUID,
        approve_data: RCAApproveRequest,
        current_user: User,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> RCARead:
        """
        Approves RCA investigation with 21 CFR Part 11 password re-authentication.
        """
        rca = await RCAService.get_rca_or_404(db, rca_id)
        if rca.status == "APPROVED":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"RCA {rca.rca_number} is already APPROVED.",
            )

        sig_payload = ElectronicSignatureCreate(
            password=approve_data.password,
            reason=approve_data.reason,
            action="RCA Approval",
            target_status="APPROVED",
        )
        await create_signature(
            db=db,
            complaint_id=rca.complaint_id,
            payload=sig_payload,
            current_user=current_user,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        now = datetime.now(timezone.utc)
        rca.status = "APPROVED"
        rca.approved_by = current_user.full_name or current_user.email
        rca.approved_at = now
        rca.updated_by = current_user.full_name or current_user.email
        rca.updated_at = now

        await log_audit_event(
            db=db,
            action_type="RCA Approved",
            description=f"Approved RCA {rca.rca_number} with 21 CFR Part 11 electronic signature.",
            actor_email=current_user.email,
            complaint_id=rca.complaint_id,
            metadata={"rca_id": str(rca.id), "rca_number": rca.rca_number},
        )

        await db.commit()
        await db.refresh(rca)
        comp_number = rca.complaint.complaint_id if rca.complaint else None
        return RCAService._to_read_schema(rca, complaint_number=comp_number)

    @staticmethod
    async def add_fmea_item(
        db: AsyncSession,
        rca_id: UUID,
        item: FMEAAssessmentCreate,
        current_user: User,
    ) -> FMEAAssessmentRead:
        rca = await RCAService.get_rca_or_404(db, rca_id)
        creator_name = current_user.full_name or current_user.email
        rpn, risk_class = calculate_rpn(item.severity, item.occurrence, item.detection)

        fmea = FMEAAssessment(
            rca_id=rca.id,
            complaint_id=rca.complaint_id,
            failure_mode=item.failure_mode,
            effect_of_failure=item.effect_of_failure,
            severity=item.severity,
            occurrence=item.occurrence,
            detection=item.detection,
            rpn=rpn,
            risk_class=risk_class,
            recommended_action=item.recommended_action,
            created_by=creator_name,
            updated_by=creator_name,
        )
        db.add(fmea)
        await db.flush()

        await log_audit_event(
            db=db,
            action_type="FMEA Item Added",
            description=f"Added FMEA Failure Mode '{item.failure_mode}' (RPN={rpn}, Risk={risk_class}) to RCA {rca.rca_number}.",
            actor_email=current_user.email,
            complaint_id=rca.complaint_id,
        )

        await db.commit()
        await db.refresh(fmea)
        return FMEAAssessmentRead.model_validate(fmea)

    @staticmethod
    async def delete_rca(
        db: AsyncSession,
        rca_id: UUID,
        current_user: User,
    ) -> None:
        rca = await RCAService.get_rca_or_404(db, rca_id)

        await log_audit_event(
            db=db,
            action_type="RCA Deleted",
            description=f"Deleted RCA investigation {rca.rca_number}.",
            actor_email=current_user.email,
            complaint_id=rca.complaint_id,
        )

        await db.delete(rca)
        await db.commit()

    @staticmethod
    async def has_any_rca_for_complaint(db: AsyncSession, complaint_id: UUID) -> bool:
        """
        Returns True if complaint has any RCA record (draft or approved).
        """
        stmt = select(RCARecord).where(RCARecord.complaint_id == complaint_id)
        res = await db.execute(stmt)
        return res.scalar_one_or_none() is not None

    @staticmethod
    async def is_rca_approved_for_complaint(db: AsyncSession, complaint_id: UUID) -> bool:

        """
        Returns True if complaint has at least one APPROVED RCA record.
        """
        stmt = select(RCARecord).where(RCARecord.complaint_id == complaint_id, RCARecord.status == "APPROVED")
        res = await db.execute(stmt)
        return res.scalar_one_or_none() is not None

    @staticmethod
    async def list_rcas(
        db: AsyncSession,
        page: int = 1,
        page_size: int = 10,
        status: Optional[str] = None,
        category: Optional[str] = None,
        complaint_id: Optional[UUID] = None,
        search: Optional[str] = None,
    ) -> RCAListResponse:
        stmt = select(RCARecord)

        filters = []
        if status:
            filters.append(RCARecord.status == status)
        if category:
            filters.append(RCARecord.root_cause_category == category)
        if complaint_id:
            filters.append(RCARecord.complaint_id == complaint_id)
        if search:
            pattern = f"%{search}%"
            filters.append(
                or_(
                    RCARecord.rca_number.ilike(pattern),
                    RCARecord.primary_root_cause.ilike(pattern),
                    RCARecord.root_cause_category.ilike(pattern),
                )
            )

        if filters:
            stmt = stmt.where(*filters)

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = (await db.execute(count_stmt)).scalar_one() or 0

        stmt = stmt.order_by(RCARecord.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
        rcas = (await db.execute(stmt)).scalars().all()

        items = [
            RCAService._to_read_schema(r, complaint_number=r.complaint.complaint_id if r.complaint else None)
            for r in rcas
        ]
        total_pages = (total + page_size - 1) // page_size if total > 0 else 1

        return RCAListResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    @staticmethod
    async def get_dashboard_metrics(db: AsyncSession) -> RCADashboardRead:
        stmt = select(RCARecord)
        rcas = (await db.execute(stmt)).scalars().all()

        fmea_stmt = select(FMEAAssessment)
        fmeas = (await db.execute(fmea_stmt)).scalars().all()

        total_rcas = len(rcas)
        approved = sum(1 for r in rcas if r.status == "APPROVED")
        pending = sum(1 for r in rcas if r.status in ("DRAFT", "UNDER_REVIEW"))

        high_risk_fmea = sum(1 for f in fmeas if f.rpn >= 200 or f.severity >= 8)
        avg_rpn = round(sum(f.rpn for f in fmeas) / len(fmeas), 1) if fmeas else 0.0

        cat_counts: Dict[str, int] = {}
        meth_counts: Dict[str, int] = {}

        for r in rcas:
            cat_counts[r.root_cause_category] = cat_counts.get(r.root_cause_category, 0) + 1
            meth_counts[r.methodology] = meth_counts.get(r.methodology, 0) + 1

        return RCADashboardRead(
            total_rcas=total_rcas,
            approved_rcas=approved,
            pending_rcas=pending,
            high_risk_fmea_count=high_risk_fmea,
            average_rpn=avg_rpn,
            by_category=cat_counts,
            by_methodology=meth_counts,
        )

    @staticmethod
    def _to_read_schema(rca: RCARecord, complaint_number: Optional[str] = None) -> RCARead:
        whys = [FiveWhyItem(**item) for item in json.loads(rca.five_whys_json)] if rca.five_whys_json else None
        fish = FishboneCategories(**json.loads(rca.fishbone_json)) if rca.fishbone_json else None
        fmea_list = [FMEAAssessmentRead.model_validate(f) for f in rca.fmea_items]

        return RCARead(
            id=rca.id,
            complaint_id=rca.complaint_id,
            complaint_number=complaint_number,
            rca_number=rca.rca_number,
            methodology=rca.methodology,
            primary_root_cause=rca.primary_root_cause,
            root_cause_category=rca.root_cause_category,
            five_whys=whys,
            fishbone=fish,
            contributing_factors=rca.contributing_factors,
            status=rca.status,
            approved_by=rca.approved_by,
            approved_at=rca.approved_at,
            created_by=rca.created_by,
            updated_by=rca.updated_by,
            created_at=rca.created_at,
            updated_at=rca.updated_at,
            fmea_items=fmea_list,
        )
