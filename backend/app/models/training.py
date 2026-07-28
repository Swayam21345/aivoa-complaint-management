import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, List, Optional
from uuid import UUID

from sqlalchemy import Boolean, CHAR, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base



if TYPE_CHECKING:
    from app.models.user import User
    from app.models.document import Document
    from app.models.signature import ElectronicSignature


def generate_uuid() -> str:
    return str(uuid.uuid4())


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


class TrainingCourse(Base):
    __tablename__ = "training_courses"

    id: Mapped[UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4, index=True
    )
    course_number: Mapped[str] = mapped_column(
        String(50), unique=True, index=True, nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    category: Mapped[str] = mapped_column(String(100), default="QUALITY")
    training_type: Mapped[str] = mapped_column(
        String(50), default="SOP"
    )  # SOP, CAPA, RCA, GENERAL, QUALITY, SAFETY
    duration_minutes: Mapped[int] = mapped_column(Integer, default=30)
    passing_score: Mapped[float] = mapped_column(Float, default=80.0)
    validity_days: Mapped[int] = mapped_column(Integer, default=365)
    status: Mapped[str] = mapped_column(
        String(50), default="DRAFT"
    )  # DRAFT, ACTIVE, RETIRED
    created_by: Mapped[str] = mapped_column(String(255), nullable=False)
    updated_by: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=now_utc
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=now_utc, onupdate=now_utc
    )

    # Relationships using lazy="noload"
    assignments: Mapped[List["TrainingAssignment"]] = relationship(
        "TrainingAssignment", back_populates="course", cascade="all, delete-orphan", lazy="noload"
    )
    quizzes: Mapped[List["Quiz"]] = relationship(
        "Quiz", back_populates="course", cascade="all, delete-orphan", lazy="noload"
    )


class TrainingAssignment(Base):
    __tablename__ = "training_assignments"

    id: Mapped[UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4, index=True
    )
    course_id: Mapped[UUID] = mapped_column(
        ForeignKey("training_courses.id", ondelete="CASCADE"), index=True, nullable=False
    )
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    assigned_by: Mapped[str] = mapped_column(String(255), nullable=False)
    assigned_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=now_utc
    )
    due_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[str] = mapped_column(
        String(50), default="NOT_STARTED"
    )  # NOT_STARTED, IN_PROGRESS, COMPLETED, FAILED, OVERDUE
    completion_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    electronic_signature_id: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey("electronic_signatures.id", ondelete="SET NULL"), nullable=True
    )

    # Relationships
    course: Mapped["TrainingCourse"] = relationship("TrainingCourse", back_populates="assignments", lazy="noload")
    user: Mapped["User"] = relationship("User", lazy="noload")
    signature: Mapped[Optional["ElectronicSignature"]] = relationship("ElectronicSignature", lazy="noload")


class Quiz(Base):
    __tablename__ = "quizzes"

    id: Mapped[UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4, index=True
    )
    course_id: Mapped[UUID] = mapped_column(
        ForeignKey("training_courses.id", ondelete="CASCADE"), index=True, nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    passing_score: Mapped[float] = mapped_column(Float, default=80.0)
    randomize_questions: Mapped[bool] = mapped_column(Boolean, default=True)
    time_limit_minutes: Mapped[int] = mapped_column(Integer, default=15)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=now_utc
    )

    # Relationships
    course: Mapped["TrainingCourse"] = relationship("TrainingCourse", back_populates="quizzes", lazy="noload")
    questions: Mapped[List["QuizQuestion"]] = relationship(
        "QuizQuestion", back_populates="quiz", cascade="all, delete-orphan", lazy="noload"
    )
    attempts: Mapped[List["QuizAttempt"]] = relationship(
        "QuizAttempt", back_populates="quiz", cascade="all, delete-orphan", lazy="noload"
    )


class QuizQuestion(Base):
    __tablename__ = "quiz_questions"

    id: Mapped[UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4, index=True
    )
    quiz_id: Mapped[UUID] = mapped_column(
        ForeignKey("quizzes.id", ondelete="CASCADE"), index=True, nullable=False
    )
    question: Mapped[str] = mapped_column(Text, nullable=False)
    option_a: Mapped[str] = mapped_column(String(255), nullable=False)
    option_b: Mapped[str] = mapped_column(String(255), nullable=False)
    option_c: Mapped[str] = mapped_column(String(255), nullable=False)
    option_d: Mapped[str] = mapped_column(String(255), nullable=False)
    correct_answer: Mapped[str] = mapped_column(String(10), nullable=False)  # A, B, C, D
    explanation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    display_order: Mapped[int] = mapped_column(Integer, default=1)

    quiz: Mapped["Quiz"] = relationship("Quiz", back_populates="questions", lazy="noload")


class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"

    id: Mapped[UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4, index=True
    )
    quiz_id: Mapped[UUID] = mapped_column(
        ForeignKey("quizzes.id", ondelete="CASCADE"), index=True, nullable=False
    )
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    score: Mapped[float] = mapped_column(Float, nullable=False)
    passed: Mapped[bool] = mapped_column(Boolean, nullable=False)
    attempted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=now_utc
    )

    quiz: Mapped["Quiz"] = relationship("Quiz", back_populates="attempts", lazy="noload")
    user: Mapped["User"] = relationship("User", lazy="noload")


class SOPAcknowledgement(Base):
    __tablename__ = "sop_acknowledgements"

    id: Mapped[UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4, index=True
    )
    document_id: Mapped[UUID] = mapped_column(
        ForeignKey("documents.id", ondelete="CASCADE"), index=True, nullable=False
    )
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    signature_id: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey("electronic_signatures.id", ondelete="SET NULL"), nullable=True
    )
    acknowledged_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=now_utc
    )

    document: Mapped["Document"] = relationship("Document", lazy="noload")
    user: Mapped["User"] = relationship("User", lazy="noload")
    signature: Mapped[Optional["ElectronicSignature"]] = relationship("ElectronicSignature", lazy="noload")


class CompetencyRecord(Base):
    __tablename__ = "competency_records"

    id: Mapped[UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4, index=True
    )
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    skill: Mapped[str] = mapped_column(String(150), nullable=False)
    level: Mapped[str] = mapped_column(
        String(50), default="BEGINNER"
    )  # BEGINNER, INTERMEDIATE, ADVANCED, EXPERT
    verified_by: Mapped[str] = mapped_column(String(255), nullable=False)
    verified_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=now_utc
    )

    user: Mapped["User"] = relationship("User", lazy="noload")

