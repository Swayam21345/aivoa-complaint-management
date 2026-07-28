from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


# ─── Training Course Schemas ──────────────────────────────────────────────────
class TrainingCourseBase(BaseModel):
    title: str = Field(..., max_length=255)
    description: Optional[str] = None
    category: str = Field("QUALITY", max_length=100)
    training_type: str = Field("SOP", max_length=50)  # SOP, CAPA, RCA, GENERAL, QUALITY, SAFETY
    duration_minutes: int = Field(30, ge=1)
    passing_score: float = Field(80.0, ge=0.0, le=100.0)
    validity_days: int = Field(365, ge=1)


class TrainingCourseCreate(TrainingCourseBase):
    pass


class TrainingCourseUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    training_type: Optional[str] = None
    duration_minutes: Optional[int] = None
    passing_score: Optional[float] = None
    validity_days: Optional[int] = None
    status: Optional[str] = None  # DRAFT, ACTIVE, RETIRED


class QuizQuestionRead(BaseModel):
    id: UUID
    quiz_id: UUID
    question: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    explanation: Optional[str] = None
    display_order: int

    class Config:
        from_attributes = True


class QuizQuestionCreate(BaseModel):
    question: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    correct_answer: str = Field(..., pattern="^[A-Da-d]$")
    explanation: Optional[str] = None
    display_order: int = 1


class QuizCreate(BaseModel):
    title: str
    passing_score: float = 80.0
    randomize_questions: bool = True
    time_limit_minutes: int = 15
    questions: List[QuizQuestionCreate] = []


class QuizRead(BaseModel):
    id: UUID
    course_id: UUID
    title: str
    passing_score: float
    randomize_questions: bool
    time_limit_minutes: int
    created_at: datetime
    questions: List[QuizQuestionRead] = []

    class Config:
        from_attributes = True


class TrainingCourseRead(TrainingCourseBase):
    id: UUID
    course_number: str
    status: str
    created_by: str
    updated_by: str
    created_at: datetime
    updated_at: datetime
    quizzes: List[QuizRead] = []

    class Config:
        from_attributes = True


# ─── Assignments & Quiz Attempts Schemas ──────────────────────────────────────
class TrainingAssignmentCreate(BaseModel):
    user_id: UUID
    due_days: int = Field(30, ge=1)


class BulkAssignmentCreate(BaseModel):
    user_ids: List[UUID]
    due_days: int = Field(30, ge=1)


class TrainingAssignmentRead(BaseModel):
    id: UUID
    course_id: UUID
    user_id: UUID
    assigned_by: str
    assigned_date: datetime
    due_date: datetime
    status: str  # NOT_STARTED, IN_PROGRESS, COMPLETED, FAILED, OVERDUE
    completion_date: Optional[datetime] = None
    score: Optional[float] = None
    attempts: int
    electronic_signature_id: Optional[UUID] = None
    course: Optional[TrainingCourseRead] = None
    user_email: Optional[str] = None
    user_full_name: Optional[str] = None

    class Config:
        from_attributes = True


class QuizAnswerSubmit(BaseModel):
    question_id: UUID
    selected_option: str  # A, B, C, D


class QuizAttemptCreate(BaseModel):
    answers: List[QuizAnswerSubmit]


class QuizAttemptRead(BaseModel):
    id: UUID
    quiz_id: UUID
    user_id: UUID
    score: float
    passed: bool
    attempted_at: datetime

    class Config:
        from_attributes = True


class SOPAcknowledgementCreate(BaseModel):
    document_id: UUID
    password: str
    reason: str = Field("SOP Reading & Understanding Acknowledgement", min_length=1)


class SOPAcknowledgementRead(BaseModel):
    id: UUID
    document_id: UUID
    user_id: UUID
    signature_id: Optional[UUID] = None
    acknowledged_at: datetime

    class Config:
        from_attributes = True


class CompetencyCreate(BaseModel):
    user_id: UUID
    skill: str = Field(..., max_length=150)
    level: str = Field("BEGINNER", max_length=50)  # BEGINNER, INTERMEDIATE, ADVANCED, EXPERT


class CompetencyRead(BaseModel):
    id: UUID
    user_id: UUID
    skill: str
    level: str
    verified_by: str
    verified_at: datetime
    user_full_name: Optional[str] = None

    class Config:
        from_attributes = True


class TrainingDashboardRead(BaseModel):
    total_courses: int
    active_courses: int
    total_assignments: int
    completed_assignments: int
    overdue_assignments: int
    in_progress_assignments: int
    completion_rate_percentage: float
    average_quiz_score: float
    department_compliance: Dict[str, float]
    status_distribution: Dict[str, int]
    by_category: Dict[str, int]
    top_failed_courses: List[Dict[str, str]]


class TrainingReportRead(BaseModel):
    total_records: int
    completed_count: int
    overdue_count: int
    expired_certifications_count: int
    competency_matrix: List[CompetencyRead]
    assignments: List[TrainingAssignmentRead]
