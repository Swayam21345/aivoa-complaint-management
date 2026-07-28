from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.complaint import Complaint
from app.models.reviewer_note import ReviewerNote
from app.schemas.reviewer_note import ReviewerNoteCreate, ReviewerNoteUpdate


class ReviewerNoteService:
    """Business logic for Managing Reviewer Notes on Complaints."""

    @staticmethod
    async def create_note(
        db: AsyncSession,
        complaint_id: UUID,
        payload: ReviewerNoteCreate,
    ) -> ReviewerNote:
        # Check complaint exists and is not deleted
        res = await db.execute(
            select(Complaint).where(
                Complaint.id == complaint_id,
                Complaint.is_deleted == False,  # noqa: E712
            )
        )
        complaint = res.scalar_one_or_none()
        if not complaint:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Complaint with ID '{complaint_id}' not found.",
            )

        note = ReviewerNote(
            complaint_id=complaint_id,
            author=payload.author,
            content=payload.content,
        )
        db.add(note)
        await db.flush()
        await db.refresh(note)
        return note

    @staticmethod
    async def list_notes(
        db: AsyncSession,
        complaint_id: UUID,
    ) -> list[ReviewerNote]:
        res = await db.execute(
            select(ReviewerNote)
            .where(
                ReviewerNote.complaint_id == complaint_id,
                ReviewerNote.is_deleted == False,  # noqa: E712
            )
            .order_by(ReviewerNote.created_at.desc())
        )
        return list(res.scalars().all())

    @staticmethod
    async def update_note(
        db: AsyncSession,
        complaint_id: UUID,
        note_id: UUID,
        payload: ReviewerNoteUpdate,
    ) -> ReviewerNote:
        res = await db.execute(
            select(ReviewerNote).where(
                ReviewerNote.id == note_id,
                ReviewerNote.complaint_id == complaint_id,
                ReviewerNote.is_deleted == False,  # noqa: E712
            )
        )
        note = res.scalar_one_or_none()
        if not note:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Reviewer note '{note_id}' not found for complaint '{complaint_id}'.",
            )

        note.content = payload.content
        note.updated_at = datetime.now(timezone.utc)
        await db.flush()
        await db.refresh(note)
        return note

    @staticmethod
    async def delete_note(
        db: AsyncSession,
        complaint_id: UUID,
        note_id: UUID,
    ) -> None:
        res = await db.execute(
            select(ReviewerNote).where(
                ReviewerNote.id == note_id,
                ReviewerNote.complaint_id == complaint_id,
                ReviewerNote.is_deleted == False,  # noqa: E712
            )
        )
        note = res.scalar_one_or_none()
        if not note:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Reviewer note '{note_id}' not found for complaint '{complaint_id}'.",
            )

        note.is_deleted = True
        note.updated_at = datetime.now(timezone.utc)
        await db.flush()
