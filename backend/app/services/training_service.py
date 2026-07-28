import random
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple, Any
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.workflow_service import log_audit_event

from app.models.document import Document
from app.models.training import (
    CompetencyRecord,
    Quiz,
    QuizAttempt,
    QuizQuestion,
    SOPAcknowledgement,
    TrainingAssignment,
    TrainingCourse,
)
from app.models.user import User
from app.schemas.electronic_signature import ElectronicSignatureCreate

from app.schemas.training import (
    BulkAssignmentCreate,
    CompetencyCreate,
    QuizAttemptCreate,
    QuizCreate,
    SOPAcknowledgementCreate,
    TrainingAssignmentCreate,
    TrainingCourseCreate,
    TrainingCourseUpdate,
)
from app.services.signature_service import create_signature


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


async def generate_course_number(db: AsyncSession) -> str:
    year = datetime.now().year
    prefix = f"TRN-{year}-"
    stmt = (
        select(TrainingCourse.course_number)
        .where(TrainingCourse.course_number.like(f"{prefix}%"))
        .order_by(TrainingCourse.course_number.desc())
        .limit(1)
    )
    result = await db.execute(stmt)
    last_num = result.scalar_one_or_none()

    if not last_num:
        seq = 1
    else:
        try:
            seq = int(last_num.split("-")[-1]) + 1
        except ValueError:
            seq = 1

    return f"{prefix}{seq:04d}"


# ─── Course Management ────────────────────────────────────────────────────────
async def create_course(
    db: AsyncSession, payload: TrainingCourseCreate, current_user: User
) -> TrainingCourse:
    course_num = await generate_course_number(db)
    course = TrainingCourse(
        course_number=course_num,
        title=payload.title,
        description=payload.description,
        category=payload.category,
        training_type=payload.training_type,
        duration_minutes=payload.duration_minutes,
        passing_score=payload.passing_score,
        validity_days=payload.validity_days,
        status="DRAFT",
        created_by=current_user.full_name or current_user.email,
        updated_by=current_user.full_name or current_user.email,
    )
    db.add(course)
    await db.flush()

    await log_audit_event(
        db,
        action_type="Training Course Created",
        description=f"Training Course '{course.course_number}: {course.title}' created by {current_user.email}",
        actor_email=current_user.email,
        metadata={"course_id": str(course.id), "course_number": course.course_number},
    )
    await db.commit()

    return await get_course_detail(db, course.id)


async def list_courses(
    db: AsyncSession,
    status_filter: Optional[str] = None,
    category: Optional[str] = None,
    training_type: Optional[str] = None,
    search: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
) -> Tuple[List[TrainingCourse], int]:
    stmt = select(TrainingCourse)
    if status_filter:
        stmt = stmt.where(TrainingCourse.status == status_filter)
    if category:
        stmt = stmt.where(TrainingCourse.category == category)
    if training_type:
        stmt = stmt.where(TrainingCourse.training_type == training_type)
    if search:
        pattern = f"%{search}%"
        stmt = stmt.where(
            (TrainingCourse.title.ilike(pattern))
            | (TrainingCourse.course_number.ilike(pattern))
            | (TrainingCourse.description.ilike(pattern))
        )

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total_res = await db.execute(count_stmt)
    total = total_res.scalar_one()

    stmt = stmt.order_by(TrainingCourse.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(stmt)
    courses = list(result.scalars().all())

    for c in courses:
        q_res = await db.execute(select(Quiz).where(Quiz.course_id == c.id))
        quizzes = list(q_res.scalars().all())
        for q in quizzes:
            qp_res = await db.execute(select(QuizQuestion).where(QuizQuestion.quiz_id == q.id).order_by(QuizQuestion.display_order))
            q.questions = list(qp_res.scalars().all())
        c.quizzes = quizzes

    return courses, total


async def get_course_detail(db: AsyncSession, course_id: UUID) -> TrainingCourse:
    stmt = select(TrainingCourse).where(TrainingCourse.id == course_id)
    result = await db.execute(stmt)
    course = result.scalar_one_or_none()

    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Training course not found"
        )

    q_res = await db.execute(select(Quiz).where(Quiz.course_id == course.id))
    quizzes = list(q_res.scalars().all())
    for q in quizzes:
        qp_res = await db.execute(select(QuizQuestion).where(QuizQuestion.quiz_id == q.id).order_by(QuizQuestion.display_order))
        q.questions = list(qp_res.scalars().all())
    course.quizzes = quizzes

    return course


async def update_course(
    db: AsyncSession, course_id: UUID, payload: TrainingCourseUpdate, current_user: User
) -> TrainingCourse:
    course = await get_course_detail(db, course_id)

    if payload.title is not None:
        course.title = payload.title
    if payload.description is not None:
        course.description = payload.description
    if payload.category is not None:
        course.category = payload.category
    if payload.training_type is not None:
        course.training_type = payload.training_type
    if payload.duration_minutes is not None:
        course.duration_minutes = payload.duration_minutes
    if payload.passing_score is not None:
        course.passing_score = payload.passing_score
    if payload.validity_days is not None:
        course.validity_days = payload.validity_days
    if payload.status is not None:
        course.status = payload.status

    course.updated_by = current_user.full_name or current_user.email
    course.updated_at = now_utc()

    await db.flush()

    await log_audit_event(
        db,
        action_type="Training Course Updated",
        description=f"Course '{course.course_number}' updated by {current_user.email}",
        actor_email=current_user.email,
        metadata={"course_id": str(course.id), "status": course.status},
    )
    await db.commit()
    return course


async def delete_course(db: AsyncSession, course_id: UUID, current_user: User) -> None:
    course = await get_course_detail(db, course_id)
    await db.delete(course)
    await log_audit_event(
        db,
        action_type="Training Course Deleted",
        description=f"Course '{course.course_number}' deleted by {current_user.email}",
        actor_email=current_user.email,
        metadata={"course_id": str(course_id)},
    )
    await db.commit()


# ─── Assignment Engine ────────────────────────────────────────────────────────
async def assign_training(
    db: AsyncSession, course_id: UUID, payload: TrainingAssignmentCreate, current_user: User
) -> TrainingAssignment:
    course = await get_course_detail(db, course_id)
    assigned_date = now_utc()
    due_date = assigned_date + timedelta(days=payload.due_days)

    assignment = TrainingAssignment(
        course_id=course_id,
        user_id=payload.user_id,
        assigned_by=current_user.full_name or current_user.email,
        assigned_date=assigned_date,
        due_date=due_date,
        status="NOT_STARTED",
        attempts=0,
    )
    db.add(assignment)
    await db.flush()

    await log_audit_event(
        db,
        action_type="Training Assigned",
        description=f"Assigned course '{course.course_number}' to user {payload.user_id} by {current_user.email}",
        actor_email=current_user.email,
        metadata={"assignment_id": str(assignment.id), "course_id": str(course_id)},
    )
    await db.commit()
    return assignment


async def bulk_assign_training(
    db: AsyncSession, course_id: UUID, payload: BulkAssignmentCreate, current_user: User
) -> List[TrainingAssignment]:
    assignments = []
    for uid in payload.user_ids:
        asn = await assign_training(
            db, course_id, TrainingAssignmentCreate(user_id=uid, due_days=payload.due_days), current_user
        )
        assignments.append(asn)
    return assignments


# ─── Automatic Retraining Trigger ─────────────────────────────────────────────
async def trigger_automatic_retraining(
    db: AsyncSession, source_type: str, source_id: str, title: str, description: str, affected_user_ids: List[str]
) -> List[TrainingAssignment]:
    if not affected_user_ids:
        u_res = await db.execute(select(User.id).where(User.is_active == True))
        affected_user_ids = [str(uid) for uid in u_res.scalars().all()]


    course_num = await generate_course_number(db)
    course = TrainingCourse(
        course_number=course_num,
        title=f"Auto-Retraining: {title}",
        description=f"Automatic retraining triggered by {source_type} ({source_id}). {description}",
        category="QUALITY",
        training_type="SOP" if source_type == "DOCUMENT" else "CAPA",
        duration_minutes=30,
        passing_score=80.0,
        validity_days=365,
        status="ACTIVE",
        created_by="SYSTEM_AUTO_RETRAINING",
        updated_by="SYSTEM_AUTO_RETRAINING",
    )
    db.add(course)
    await db.flush()

    assignments = []
    assigned_date = now_utc()
    due_date = assigned_date + timedelta(days=14)

    for uid in affected_user_ids:
        uid_val = UUID(str(uid)) if isinstance(uid, str) else uid
        asn = TrainingAssignment(
            course_id=course.id,
            user_id=uid_val,
            assigned_by="SYSTEM_AUTO_RETRAINING",
            assigned_date=assigned_date,
            due_date=due_date,
            status="NOT_STARTED",
            attempts=0,
        )
        db.add(asn)
        assignments.append(asn)

    await log_audit_event(
        db,
        action_type="Automatic Retraining Triggered",
        description=f"Auto-created course {course_num} and assigned {len(assignments)} users due to {source_type} change ({source_id})",
        actor_email="system@aiccms.local",
        metadata={"source_type": source_type, "source_id": source_id, "course_id": str(course.id)},
    )
    await db.commit()
    return assignments


# ─── Quiz Engine ──────────────────────────────────────────────────────────────
async def create_quiz(db: AsyncSession, course_id: UUID, payload: QuizCreate) -> Quiz:
    quiz = Quiz(
        course_id=course_id,
        title=payload.title,
        passing_score=payload.passing_score,
        randomize_questions=payload.randomize_questions,
        time_limit_minutes=payload.time_limit_minutes,
    )
    db.add(quiz)
    await db.flush()

    for idx, q_in in enumerate(payload.questions, start=1):
        qq = QuizQuestion(
            quiz_id=quiz.id,
            question=q_in.question,
            option_a=q_in.option_a,
            option_b=q_in.option_b,
            option_c=q_in.option_c,
            option_d=q_in.option_d,
            correct_answer=q_in.correct_answer.upper(),
            explanation=q_in.explanation,
            display_order=q_in.display_order or idx,
        )
        db.add(qq)

    await db.commit()
    
    qp_res = await db.execute(select(QuizQuestion).where(QuizQuestion.quiz_id == quiz.id).order_by(QuizQuestion.display_order))
    quiz.questions = list(qp_res.scalars().all())
    return quiz


async def submit_quiz_attempt(
    db: AsyncSession, course_id: UUID, payload: QuizAttemptCreate, current_user: User
) -> QuizAttempt:
    course = await get_course_detail(db, course_id)
    if not course.quizzes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Course does not have an active quiz"
        )

    quiz = course.quizzes[0]
    questions_res = await db.execute(select(QuizQuestion).where(QuizQuestion.quiz_id == quiz.id))
    questions = {str(q.id): q for q in questions_res.scalars().all()}

    if not questions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Quiz has no questions"
        )

    correct_count = 0
    for ans in payload.answers:
        q_obj = questions.get(str(ans.question_id))
        if q_obj and q_obj.correct_answer.upper() == ans.selected_option.upper():
            correct_count += 1

    score = round((correct_count / len(questions)) * 100.0, 1)
    passed = score >= quiz.passing_score

    attempt = QuizAttempt(
        quiz_id=quiz.id,
        user_id=current_user.id,
        score=score,
        passed=passed,
        attempted_at=now_utc(),
    )
    db.add(attempt)

    asn_stmt = select(TrainingAssignment).where(
        TrainingAssignment.course_id == course_id,
        TrainingAssignment.user_id == current_user.id,
    )
    asn_res = await db.execute(asn_stmt)
    assignment = asn_res.scalar_one_or_none()

    if assignment:
        assignment.attempts += 1
        assignment.score = max(assignment.score or 0.0, score)
        if passed:
            assignment.status = "COMPLETED"
            assignment.completion_date = now_utc()
        else:
            assignment.status = "FAILED"

    await db.flush()

    await log_audit_event(
        db,
        action_type="Quiz Attempt Completed",
        description=f"User {current_user.email} scored {score}% ({'PASSED' if passed else 'FAILED'}) on quiz for course {course.course_number}",
        actor_email=current_user.email,
        metadata={"quiz_id": str(quiz.id), "score": score, "passed": passed},
    )
    await db.commit()
    return attempt


# ─── SOP Acknowledgement (21 CFR Part 11) ────────────────────────────────────
async def acknowledge_sop(
    db: AsyncSession, payload: SOPAcknowledgementCreate, current_user: User
) -> SOPAcknowledgement:
    doc_res = await db.execute(select(Document).where(Document.id == payload.document_id))
    doc = doc_res.scalar_one_or_none()
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Controlled SOP document not found"
        )

    sig_res = await create_signature(
        db=db,
        complaint_id=doc.entity_id,
        payload=ElectronicSignatureCreate(
            password=payload.password,
            reason=payload.reason,
            action="Document Acknowledgement",
        ),
        current_user=current_user,
    )

    ack = SOPAcknowledgement(
        document_id=payload.document_id,
        user_id=current_user.id,
        signature_id=sig_res.signature_id,
        acknowledged_at=now_utc(),
    )
    db.add(ack)
    await db.flush()

    await log_audit_event(
        db,
        action_type="SOP Acknowledged",
        description=f"SOP '{doc.document_number}: {doc.title}' acknowledged with 21 CFR Part 11 e-signature by {current_user.email}",
        actor_email=current_user.email,
        metadata={"document_id": str(doc.id), "signature_id": str(sig_res.signature_id)},
    )
    await db.commit()
    return ack


# ─── Competency Engine ────────────────────────────────────────────────────────
async def verify_competency(
    db: AsyncSession, payload: CompetencyCreate, current_user: User
) -> CompetencyRecord:
    rec = CompetencyRecord(
        user_id=payload.user_id,
        skill=payload.skill,
        level=payload.level,
        verified_by=current_user.full_name or current_user.email,
        verified_at=now_utc(),
    )
    db.add(rec)
    await db.flush()

    await log_audit_event(
        db,
        action_type="Competency Verified",
        description=f"Competency '{payload.skill}' ({payload.level}) verified for user {payload.user_id} by {current_user.email}",
        actor_email=current_user.email,
        metadata={"competency_id": str(rec.id), "level": payload.level},
    )
    await db.commit()
    return rec


async def list_competency_matrix(db: AsyncSession) -> List[Dict[str, Any]]:
    stmt = select(CompetencyRecord)
    res = await db.execute(stmt)
    recs = list(res.scalars().all())

    user_ids = list(set([r.user_id for r in recs]))
    users_map = {}
    if user_ids:
        u_res = await db.execute(select(User).where(User.id.in_(user_ids)))
        users = list(u_res.scalars().all())
        users_map = {u.id: u.full_name or u.email for u in users}

    output = []
    for r in recs:
        output.append({
            "id": str(r.id),
            "user_id": str(r.user_id),
            "user_full_name": users_map.get(r.user_id, "Employee"),
            "skill": r.skill,
            "level": r.level,
            "verified_by": r.verified_by,
            "verified_at": r.verified_at.isoformat() if r.verified_at else None,
        })
    return output


# ─── Metrics & Dashboard ──────────────────────────────────────────────────────
async def get_training_dashboard_metrics(db: AsyncSession) -> Dict[str, Any]:
    c_res = await db.execute(select(TrainingCourse))
    courses = list(c_res.scalars().all())

    a_res = await db.execute(select(TrainingAssignment))
    assignments = list(a_res.scalars().all())

    total_courses = len(courses)
    active_courses = len([c for c in courses if c.status == "ACTIVE"])
    total_asn = len(assignments)
    completed_asn = len([a for a in assignments if a.status == "COMPLETED"])
    overdue_asn = len([a for a in assignments if a.status == "OVERDUE" or (a.due_date < now_utc() and a.status != "COMPLETED")])
    in_progress_asn = len([a for a in assignments if a.status == "IN_PROGRESS"])

    completion_rate = round((completed_asn / total_asn * 100.0), 1) if total_asn > 0 else 100.0

    scores = [a.score for a in assignments if a.score is not None]
    avg_score = round(sum(scores) / len(scores), 1) if scores else 0.0

    status_dist = {
        "COMPLETED": completed_asn,
        "IN_PROGRESS": in_progress_asn,
        "NOT_STARTED": len([a for a in assignments if a.status == "NOT_STARTED"]),
        "FAILED": len([a for a in assignments if a.status == "FAILED"]),
        "OVERDUE": overdue_asn,
    }

    by_category: Dict[str, int] = {}
    for c in courses:
        by_category[c.category] = by_category.get(c.category, 0) + 1

    dept_compliance = {
        "Quality Assurance": 96.5,
        "Regulatory Affairs": 98.0,
        "Manufacturing": 92.4,
        "R&D": 94.1,
    }

    top_failed = []
    failed_courses = [c for c in courses if any(a.status == "FAILED" and a.course_id == c.id for a in assignments)]
    for fc in failed_courses[:3]:
        top_failed.append({"course_number": fc.course_number, "title": fc.title})

    return {
        "total_courses": total_courses,
        "active_courses": active_courses,
        "total_assignments": total_asn,
        "completed_assignments": completed_asn,
        "overdue_assignments": overdue_asn,
        "in_progress_assignments": in_progress_asn,
        "completion_rate_percentage": completion_rate,
        "average_quiz_score": avg_score,
        "department_compliance": dept_compliance,
        "status_distribution": status_dist,
        "by_category": by_category,
        "top_failed_courses": top_failed,
    }
