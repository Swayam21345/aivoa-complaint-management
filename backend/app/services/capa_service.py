from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.capa import CAPARecord
from app.models.complaint import Complaint
from app.models.user import User
from app.schemas.capa import (
    CAPACloseRequest,
    CAPACreate,
    CAPADashboardRead,
    CAPAEffectivenessReview,
    CAPAListResponse,
    CAPARead,
    CAPATrendItem,
    CAPAUpdate,
)
from app.schemas.electronic_signature import ElectronicSignatureCreate
from app.services.signature_service import create_signature
from app.services.workflow_service import log_audit_event


VALID_CAPA_STATUSES = {
    "OPEN",
    "UNDER_IMPLEMENTATION",
    "PENDING_EFFECTIVENESS",
    "EFFECTIVE",
    "INEFFECTIVE",
    "CLOSED",
    "CANCELLED",
}

# Allowed status transitions
CAPA_TRANSITIONS = {
    "OPEN": {"UNDER_IMPLEMENTATION", "CANCELLED"},
    "UNDER_IMPLEMENTATION": {"PENDING_EFFECTIVENESS", "CANCELLED", "OPEN"},
    "PENDING_EFFECTIVENESS": {"EFFECTIVE", "INEFFECTIVE", "UNDER_IMPLEMENTATION", "CANCELLED"},
    "EFFECTIVE": {"CLOSED", "UNDER_IMPLEMENTATION", "CANCELLED"},
    "INEFFECTIVE": {"UNDER_IMPLEMENTATION", "OPEN", "CANCELLED"},
    "CLOSED": set(),  # Terminal
    "CANCELLED": set(),  # Terminal
}


class CAPAService:
    @staticmethod
    async def generate_capa_number(db: AsyncSession) -> str:
        """
        Generates auto-incremented CAPA number format: CAPA-YYYY-XXXX.
        """
        year_str = datetime.now(timezone.utc).strftime("%Y")
        prefix = f"CAPA-{year_str}-"
        
        stmt = select(func.count()).select_from(CAPARecord).where(CAPARecord.capa_number.like(f"{prefix}%"))
        count = (await db.execute(stmt)).scalar_one() or 0
        return f"{prefix}{count + 1:04d}"

    @staticmethod
    async def get_capa_or_404(db: AsyncSession, capa_id: UUID) -> CAPARecord:
        stmt = select(CAPARecord).where(CAPARecord.id == capa_id)
        res = await db.execute(stmt)
        capa = res.scalar_one_or_none()
        if not capa:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"CAPA record with ID '{capa_id}' not found.",
            )
        return capa

    @staticmethod
    async def create_capa(
        db: AsyncSession,
        payload: CAPACreate,
        current_user: User,
    ) -> CAPARead:
        # Check complaint existence
        comp_stmt = select(Complaint).where(Complaint.id == payload.complaint_id, Complaint.is_deleted == False)  # noqa: E712
        comp_res = await db.execute(comp_stmt)
        complaint = comp_res.scalar_one_or_none()
        if not complaint:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Parent complaint record '{payload.complaint_id}' not found.",
            )

        capa_number = await CAPAService.generate_capa_number(db)
        creator_name = current_user.full_name or current_user.email

        capa = CAPARecord(
            complaint_id=payload.complaint_id,
            capa_number=capa_number,
            title=payload.title,
            description=payload.description,
            root_cause=payload.root_cause,
            corrective_action=payload.corrective_action,
            preventive_action=payload.preventive_action,
            owner=payload.owner or current_user.full_name,
            reviewer=payload.reviewer,
            target_completion_date=payload.target_completion_date,
            effectiveness_due_date=payload.effectiveness_due_date,
            priority=payload.priority,
            risk_level=payload.risk_level,
            status="OPEN",
            created_by=creator_name,
            updated_by=creator_name,
        )
        db.add(capa)
        await db.flush()

        # Log audit trail
        await log_audit_event(
            db=db,
            action_type="CAPA Created",
            description=f"Created CAPA {capa_number}: '{payload.title}' for Complaint {complaint.complaint_id}.",
            actor_email=current_user.email,
            complaint_id=complaint.id,
            metadata={
                "capa_id": str(capa.id),
                "capa_number": capa_number,
                "priority": payload.priority,
                "risk_level": payload.risk_level,
            },
        )

        await db.commit()
        await db.refresh(capa)
        return CAPAService._to_read_schema(capa, complaint_number=complaint.complaint_id)

    @staticmethod
    async def get_capa_detail(db: AsyncSession, capa_id: UUID) -> CAPARead:
        capa = await CAPAService.get_capa_or_404(db, capa_id)
        comp_number = capa.complaint.complaint_id if capa.complaint else None
        return CAPAService._to_read_schema(capa, complaint_number=comp_number)

    @staticmethod
    async def update_capa(
        db: AsyncSession,
        capa_id: UUID,
        payload: CAPAUpdate,
        current_user: User,
    ) -> CAPARead:
        capa = await CAPAService.get_capa_or_404(db, capa_id)
        updater_name = current_user.full_name or current_user.email

        # Handle status transition if specified
        if payload.status and payload.status != capa.status:
            if payload.status not in VALID_CAPA_STATUSES:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid status '{payload.status}'. Valid statuses: {sorted(list(VALID_CAPA_STATUSES))}.",
                )

            allowed = CAPA_TRANSITIONS.get(capa.status, set())
            if payload.status not in allowed:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid transition from '{capa.status}' to '{payload.status}'. Allowed: {sorted(list(allowed))}.",
                )

            # Special states requiring electronic signature endpoint
            if payload.status in ("CLOSED", "EFFECTIVE"):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Status transition to '{payload.status}' requires 21 CFR Part 11 electronic signature endpoint.",
                )

            old_status = capa.status
            capa.status = payload.status

            await log_audit_event(
                db=db,
                action_type="CAPA Status Change",
                description=f"Updated CAPA {capa.capa_number} status from {old_status} to {payload.status}.",
                actor_email=current_user.email,
                complaint_id=capa.complaint_id,
                metadata={
                    "capa_id": str(capa.id),
                    "capa_number": capa.capa_number,
                    "old_status": old_status,
                    "new_status": payload.status,
                },
            )

        # Update fields
        update_data = payload.model_dump(exclude_unset=True, exclude={"status"})
        for field, value in update_data.items():
            setattr(capa, field, value)

        capa.updated_by = updater_name
        capa.updated_at = datetime.now(timezone.utc)

        await db.commit()
        await db.refresh(capa)
        comp_number = capa.complaint.complaint_id if capa.complaint else None
        return CAPAService._to_read_schema(capa, complaint_number=comp_number)

    @staticmethod
    async def delete_capa(
        db: AsyncSession,
        capa_id: UUID,
        current_user: User,
    ) -> None:
        capa = await CAPAService.get_capa_or_404(db, capa_id)
        
        await log_audit_event(
            db=db,
            action_type="CAPA Deleted",
            description=f"Deleted CAPA {capa.capa_number}: '{capa.title}'.",
            actor_email=current_user.email,
            complaint_id=capa.complaint_id,
            metadata={"capa_id": str(capa.id), "capa_number": capa.capa_number},
        )

        await db.delete(capa)
        await db.commit()

    @staticmethod
    async def list_capas(
        db: AsyncSession,
        page: int = 1,
        page_size: int = 10,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        risk_level: Optional[str] = None,
        complaint_id: Optional[UUID] = None,
        owner: Optional[str] = None,
        search: Optional[str] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> CAPAListResponse:
        stmt = select(CAPARecord)

        filters = []
        if status:
            filters.append(CAPARecord.status == status)
        if priority:
            filters.append(CAPARecord.priority == priority)
        if risk_level:
            filters.append(CAPARecord.risk_level == risk_level)
        if complaint_id:
            filters.append(CAPARecord.complaint_id == complaint_id)
        if owner:
            filters.append(func.lower(CAPARecord.owner).contains(owner.lower()))
        if search:
            search_pattern = f"%{search}%"
            filters.append(
                or_(
                    CAPARecord.capa_number.ilike(search_pattern),
                    CAPARecord.title.ilike(search_pattern),
                    CAPARecord.description.ilike(search_pattern),
                    CAPARecord.owner.ilike(search_pattern),
                )
            )

        if filters:
            stmt = stmt.where(*filters)

        # Count total
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = (await db.execute(count_stmt)).scalar_one() or 0

        # Sorting
        sort_col = getattr(CAPARecord, sort_by, CAPARecord.created_at)
        if sort_order.lower() == "asc":
            stmt = stmt.order_by(sort_col.asc())
        else:
            stmt = stmt.order_by(sort_col.desc())

        # Pagination
        stmt = stmt.offset((page - 1) * page_size).limit(page_size)
        res = await db.execute(stmt)
        capas = res.scalars().all()

        items = [
            CAPAService._to_read_schema(c, complaint_number=c.complaint.complaint_id if c.complaint else None)
            for c in capas
        ]
        total_pages = (total + page_size - 1) // page_size if total > 0 else 1

        return CAPAListResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    @staticmethod
    async def review_effectiveness(
        db: AsyncSession,
        capa_id: UUID,
        review_data: CAPAEffectivenessReview,
        current_user: User,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> CAPARead:
        """
        Submits 21 CFR Part 11 signed effectiveness review.
        Transitions status from PENDING_EFFECTIVENESS to EFFECTIVE or INEFFECTIVE.
        """
        capa = await CAPAService.get_capa_or_404(db, capa_id)
        if capa.status not in ("PENDING_EFFECTIVENESS", "UNDER_IMPLEMENTATION"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"CAPA status must be 'PENDING_EFFECTIVENESS' or 'UNDER_IMPLEMENTATION' to conduct effectiveness review. Current status: '{capa.status}'.",
            )

        new_status = "EFFECTIVE" if review_data.is_effective else "INEFFECTIVE"

        # Apply 21 CFR Part 11 signature
        sig_payload = ElectronicSignatureCreate(
            password=review_data.password,
            reason=review_data.reason,
            action="CAPA Effectiveness Review",
            target_status=new_status,
        )
        await create_signature(
            db=db,
            complaint_id=capa.complaint_id,
            payload=sig_payload,
            current_user=current_user,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        old_status = capa.status
        capa.status = new_status
        capa.effectiveness_check = review_data.effectiveness_check
        capa.reviewer = current_user.full_name or current_user.email
        capa.updated_by = current_user.full_name or current_user.email
        capa.updated_at = datetime.now(timezone.utc)

        await log_audit_event(
            db=db,
            action_type="CAPA Effectiveness Review",
            description=f"Recorded 21 CFR Part 11 signed effectiveness review for CAPA {capa.capa_number}: {new_status}.",
            actor_email=current_user.email,
            complaint_id=capa.complaint_id,
            metadata={
                "capa_id": str(capa.id),
                "capa_number": capa.capa_number,
                "old_status": old_status,
                "new_status": new_status,
                "is_effective": review_data.is_effective,
            },
        )

        await db.commit()
        await db.refresh(capa)
        comp_number = capa.complaint.complaint_id if capa.complaint else None
        return CAPAService._to_read_schema(capa, complaint_number=comp_number)

    @staticmethod
    async def close_capa(
        db: AsyncSession,
        capa_id: UUID,
        close_data: CAPACloseRequest,
        current_user: User,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> CAPARead:
        """
        Closes CAPA with 21 CFR Part 11 electronic signature.
        Requires CAPA to be in EFFECTIVE status (or UNDER_IMPLEMENTATION/OPEN if marked ready).
        """
        capa = await CAPAService.get_capa_or_404(db, capa_id)
        if capa.status == "CLOSED":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"CAPA {capa.capa_number} is already CLOSED.",
            )

        # Apply 21 CFR Part 11 signature
        sig_payload = ElectronicSignatureCreate(
            password=close_data.password,
            reason=close_data.reason,
            action="CAPA Closure",
            target_status="CLOSED",
        )
        await create_signature(
            db=db,
            complaint_id=capa.complaint_id,
            payload=sig_payload,
            current_user=current_user,
            ip_address=ip_address,
            user_agent=user_agent,
        )


        now = datetime.now(timezone.utc)
        old_status = capa.status
        capa.status = "CLOSED"
        capa.completed_date = now
        capa.updated_by = current_user.full_name or current_user.email
        capa.updated_at = now

        await log_audit_event(
            db=db,
            action_type="CAPA Closure",
            description=f"Closed CAPA {capa.capa_number} with 21 CFR Part 11 electronic signature.",
            actor_email=current_user.email,
            complaint_id=capa.complaint_id,
            metadata={
                "capa_id": str(capa.id),
                "capa_number": capa.capa_number,
                "old_status": old_status,
                "new_status": "CLOSED",
            },
        )

        await db.commit()
        await db.refresh(capa)
        comp_number = capa.complaint.complaint_id if capa.complaint else None
        return CAPAService._to_read_schema(capa, complaint_number=comp_number)

    @staticmethod
    async def are_all_complaint_capas_closed(db: AsyncSession, complaint_id: UUID) -> bool:
        """
        Checks whether all CAPAs associated with a complaint are in CLOSED status.
        Returns True if no CAPAs exist or if all existing CAPAs are CLOSED.
        """
        stmt = select(CAPARecord).where(CAPARecord.complaint_id == complaint_id)
        res = await db.execute(stmt)
        capas = res.scalars().all()
        if not capas:
            return True
        return all(c.status.upper() in ("CLOSED", "COMPLETED") for c in capas)

    @staticmethod
    async def get_dashboard_metrics(db: AsyncSession) -> CAPADashboardRead:
        """
        Calculates high-level CAPA metrics and analytics for QMS dashboards.
        """
        stmt = select(CAPARecord)
        res = await db.execute(stmt)
        capas = res.scalars().all()

        now = datetime.now(timezone.utc)
        current_month = now.month
        current_year = now.year

        open_capas = sum(1 for c in capas if c.status in ("OPEN", "UNDER_IMPLEMENTATION", "PENDING_EFFECTIVENESS", "INEFFECTIVE"))
        pending_eff = sum(1 for c in capas if c.status == "PENDING_EFFECTIVENESS")
        
        overdue = 0
        closed_this_month = 0
        closure_durations: List[float] = []

        status_counts: Dict[str, int] = {}
        priority_counts: Dict[str, int] = {}
        risk_counts: Dict[str, int] = {}

        months_map: Dict[str, Dict[str, int]] = {}
        for i in range(5, -1, -1):
            m_date = now - timedelta(days=i * 30)
            m_key = m_date.strftime("%Y-%m")
            months_map[m_key] = {"created": 0, "closed": 0}

        for c in capas:
            status_counts[c.status] = status_counts.get(c.status, 0) + 1
            priority_counts[c.priority] = priority_counts.get(c.priority, 0) + 1
            risk_counts[c.risk_level] = risk_counts.get(c.risk_level, 0) + 1

            # Overdue check
            if c.status not in ("CLOSED", "CANCELLED") and c.target_completion_date:
                t_date = c.target_completion_date if c.target_completion_date.tzinfo else c.target_completion_date.replace(tzinfo=timezone.utc)
                if now > t_date:
                    overdue += 1

            # Created month
            if c.created_at:
                c_dt = c.created_at if c.created_at.tzinfo else c.created_at.replace(tzinfo=timezone.utc)
                m_key = c_dt.strftime("%Y-%m")
                if m_key in months_map:
                    months_map[m_key]["created"] += 1

            # Closed month & closure duration
            if c.status == "CLOSED" and c.completed_date:
                comp_dt = c.completed_date if c.completed_date.tzinfo else c.completed_date.replace(tzinfo=timezone.utc)
                if comp_dt.month == current_month and comp_dt.year == current_year:
                    closed_this_month += 1

                m_key = comp_dt.strftime("%Y-%m")
                if m_key in months_map:
                    months_map[m_key]["closed"] += 1

                if c.created_at:
                    c_dt = c.created_at if c.created_at.tzinfo else c.created_at.replace(tzinfo=timezone.utc)
                    days = (comp_dt - c_dt).total_seconds() / 86400.0
                    if days >= 0:
                        closure_durations.append(days)

        avg_closure_days = round(sum(closure_durations) / len(closure_durations), 1) if closure_durations else 0.0

        monthly_trends = [
            CAPATrendItem(month=k, created=v["created"], closed=v["closed"])
            for k, v in months_map.items()
        ]

        return CAPADashboardRead(
            open_capas=open_capas,
            overdue_capas=overdue,
            pending_effectiveness=pending_eff,
            closed_this_month=closed_this_month,
            average_closure_days=avg_closure_days,
            by_status=status_counts,
            by_priority=priority_counts,
            by_risk_level=risk_counts,
            monthly_trends=monthly_trends,
        )

    @staticmethod
    def _to_read_schema(capa: CAPARecord, complaint_number: Optional[str] = None) -> CAPARead:
        return CAPARead(
            id=capa.id,
            complaint_id=capa.complaint_id,
            complaint_number=complaint_number,
            capa_number=capa.capa_number,
            title=capa.title,
            description=capa.description,
            root_cause=capa.root_cause,
            corrective_action=capa.corrective_action,
            preventive_action=capa.preventive_action,
            owner=capa.owner,
            reviewer=capa.reviewer,
            effectiveness_check=capa.effectiveness_check,
            effectiveness_due_date=capa.effectiveness_due_date,
            target_completion_date=capa.target_completion_date,
            completed_date=capa.completed_date,
            priority=capa.priority,
            risk_level=capa.risk_level,
            status=capa.status,
            created_by=capa.created_by,
            updated_by=capa.updated_by,
            created_at=capa.created_at,
            updated_at=capa.updated_at,
        )
