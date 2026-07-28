from typing import Any, Dict, List, Optional

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user, get_db, require_roles

from app.models.training import CompetencyRecord, TrainingAssignment
from app.models.user import User
from app.schemas.training import (
    BulkAssignmentCreate,
    CompetencyCreate,
    CompetencyRead,
    QuizAttemptCreate,
    QuizAttemptRead,
    QuizCreate,
    QuizRead,
    SOPAcknowledgementCreate,
    SOPAcknowledgementRead,
    TrainingAssignmentCreate,
    TrainingAssignmentRead,
    TrainingCourseCreate,
    TrainingCourseRead,
    TrainingCourseUpdate,
    TrainingDashboardRead,
    TrainingReportRead,
)
from app.services import training_service

router = APIRouter(prefix="/training", tags=["Training & Competency Management"])


@router.get("", response_model=Dict[str, Any])
async def list_training_courses(
    status_filter: Optional[str] = Query(None, alias="status"),
    category: Optional[str] = Query(None),
    training_type: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    courses, total = await training_service.list_courses(
        db, status_filter, category, training_type, search, page, page_size
    )
    return {
        "items": [TrainingCourseRead.model_validate(c) for c in courses],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.post("", response_model=TrainingCourseRead, status_code=status.HTTP_201_CREATED)
async def create_training_course(
    payload: TrainingCourseCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN", "QA_MANAGER", "HR")),
) -> TrainingCourseRead:
    course = await training_service.create_course(db, payload, current_user)
    return TrainingCourseRead.model_validate(course)


@router.get("/dashboard", response_model=TrainingDashboardRead)
async def get_training_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TrainingDashboardRead:
    metrics = await training_service.get_training_dashboard_metrics(db)
    return TrainingDashboardRead(**metrics)


@router.get("/matrix", response_model=List[Dict[str, Any]])
async def get_competency_matrix(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[Dict[str, Any]]:
    return await training_service.list_competency_matrix(db)


@router.get("/report", response_model=TrainingReportRead)
async def get_training_report(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN", "QA_MANAGER", "HR")),
) -> TrainingReportRead:
    metrics = await training_service.get_training_dashboard_metrics(db)
    
    # Load all assignments
    a_res = await db.execute(select(TrainingAssignment))
    assignments = list(a_res.scalars().all())
    
    # Load competencies
    matrix = await training_service.list_competency_matrix(db)
    comp_reads = [
        CompetencyRead(
            id=m["id"],
            user_id=m["user_id"],
            skill=m["skill"],
            level=m["level"],
            verified_by=m["verified_by"],
            verified_at=m["verified_at"],
            user_full_name=m["user_full_name"],
        ) for m in matrix
    ]

    asn_reads = []
    for a in assignments:
        asn_reads.append(
            TrainingAssignmentRead(
                id=a.id,
                course_id=a.course_id,
                user_id=a.user_id,
                assigned_by=a.assigned_by,
                assigned_date=a.assigned_date,
                due_date=a.due_date,
                status=a.status,
                completion_date=a.completion_date,
                score=a.score,
                attempts=a.attempts,
                electronic_signature_id=a.electronic_signature_id,
            )
        )

    return TrainingReportRead(
        total_records=metrics["total_assignments"],
        completed_count=metrics["completed_assignments"],
        overdue_count=metrics["overdue_assignments"],
        expired_certifications_count=0,
        competency_matrix=comp_reads,
        assignments=asn_reads,
    )


@router.get("/{id}", response_model=TrainingCourseRead)
async def get_training_course_detail(
    id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TrainingCourseRead:
    course = await training_service.get_course_detail(db, id)
    return TrainingCourseRead.model_validate(course)


@router.patch("/{id}", response_model=TrainingCourseRead)
async def update_training_course(
    id: UUID,
    payload: TrainingCourseUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN", "QA_MANAGER", "HR")),
) -> TrainingCourseRead:
    course = await training_service.update_course(db, id, payload, current_user)
    return TrainingCourseRead.model_validate(course)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_training_course(
    id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN", "QA_MANAGER")),
) -> None:
    await training_service.delete_course(db, id, current_user)


@router.post("/{id}/assign", response_model=TrainingAssignmentRead)
async def assign_training_course(
    id: UUID,
    payload: TrainingAssignmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN", "QA_MANAGER", "HR")),
) -> TrainingAssignmentRead:
    asn = await training_service.assign_training(db, id, payload, current_user)
    return TrainingAssignmentRead(
        id=asn.id,
        course_id=asn.course_id,
        user_id=asn.user_id,
        assigned_by=asn.assigned_by,
        assigned_date=asn.assigned_date,
        due_date=asn.due_date,
        status=asn.status,
        completion_date=asn.completion_date,
        score=asn.score,
        attempts=asn.attempts,
        electronic_signature_id=asn.electronic_signature_id,
    )


@router.post("/{id}/bulk-assign", response_model=List[TrainingAssignmentRead])
async def bulk_assign_training_course(
    id: UUID,
    payload: BulkAssignmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN", "QA_MANAGER", "HR")),
) -> List[TrainingAssignmentRead]:
    assignments = await training_service.bulk_assign_training(db, id, payload, current_user)
    return [
        TrainingAssignmentRead(
            id=asn.id,
            course_id=asn.course_id,
            user_id=asn.user_id,
            assigned_by=asn.assigned_by,
            assigned_date=asn.assigned_date,
            due_date=asn.due_date,
            status=asn.status,
            completion_date=asn.completion_date,
            score=asn.score,
            attempts=asn.attempts,
            electronic_signature_id=asn.electronic_signature_id,
        )
        for asn in assignments
    ]


@router.post("/{id}/quiz", response_model=QuizRead)
async def add_course_quiz(
    id: UUID,
    payload: QuizCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN", "QA_MANAGER", "HR")),
) -> QuizRead:
    quiz = await training_service.create_quiz(db, id, payload)
    return QuizRead.model_validate(quiz)


@router.post("/{id}/complete", response_model=QuizAttemptRead)
async def complete_course_quiz(
    id: UUID,
    payload: QuizAttemptCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> QuizAttemptRead:
    attempt = await training_service.submit_quiz_attempt(db, id, payload, current_user)
    return QuizAttemptRead.model_validate(attempt)


@router.post("/{id}/acknowledge", response_model=SOPAcknowledgementRead)
async def acknowledge_course_sop(
    id: UUID,
    payload: SOPAcknowledgementCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SOPAcknowledgementRead:
    ack = await training_service.acknowledge_sop(db, payload, current_user)
    return SOPAcknowledgementRead.model_validate(ack)


@router.post("/competency", response_model=CompetencyRead)
async def verify_user_competency(
    payload: CompetencyCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN", "QA_MANAGER", "HR")),
) -> CompetencyRead:
    rec = await training_service.verify_competency(db, payload, current_user)
    return CompetencyRead(
        id=rec.id,
        user_id=rec.user_id,
        skill=rec.skill,
        level=rec.level,
        verified_by=rec.verified_by,
        verified_at=rec.verified_at,
    )
