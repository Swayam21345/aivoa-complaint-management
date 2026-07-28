from typing import List, Optional
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    Query,
    Request,
    UploadFile,
    status,
)
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user, get_db, require_roles
from app.models.user import User
from app.schemas.document import (
    DocumentApproval,
    DocumentCreate,
    DocumentDashboardRead,
    DocumentListResponse,
    DocumentRead,
    DocumentUpdate,
    DocumentUploadResponse,
    DocumentVersionRead,
    DocumentVerifyResponse,
)
from app.services.document_service import DocumentService

router = APIRouter(prefix="/documents", tags=["Document Control & Evidence Management"])


@router.get(
    "",
    response_model=DocumentListResponse,
    dependencies=[Depends(require_roles("ADMIN", "QA_MANAGER", "INVESTIGATOR", "VIEWER"))],
    summary="List document evidence with pagination and filters",
)
async def list_documents(
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    category: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    entity_type: Optional[str] = Query(None),
    entity_id: Optional[UUID] = Query(None),
    search: Optional[str] = Query(None),
) -> DocumentListResponse:
    return await DocumentService.list_documents(
        db=db,
        page=page,
        page_size=page_size,
        category=category,
        status_filter=status_filter,
        entity_type=entity_type,
        entity_id=entity_id,
        search=search,
    )


@router.post(
    "/upload",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles("ADMIN", "QA_MANAGER", "INVESTIGATOR"))],
    summary="Upload a new controlled document / evidence file",
)
async def upload_document(
    file: UploadFile = File(...),
    title: str = Form(...),
    description: Optional[str] = Form(None),
    category: str = Form("Complaint Evidence"),
    entity_type: str = Form("COMPLAINT"),
    entity_id: UUID = Form(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DocumentUploadResponse:
    payload = DocumentCreate(
        title=title,
        description=description,
        category=category,
        entity_type=entity_type,
        entity_id=entity_id,
    )
    return await DocumentService.upload_document(
        db=db,
        file=file,
        create_payload=payload,
        current_user=current_user,
    )


@router.get(
    "/dashboard",
    response_model=DocumentDashboardRead,
    dependencies=[Depends(require_roles("ADMIN", "QA_MANAGER", "INVESTIGATOR", "VIEWER"))],
    summary="Get Document Control metrics and category counts",
)
async def get_document_dashboard(
    db: AsyncSession = Depends(get_db),
) -> DocumentDashboardRead:
    return await DocumentService.get_dashboard_metrics(db=db)


@router.get(
    "/{id}",
    response_model=DocumentRead,
    dependencies=[Depends(require_roles("ADMIN", "QA_MANAGER", "INVESTIGATOR", "VIEWER"))],
    summary="Get document details by ID",
)
async def get_document(
    id: UUID,
    db: AsyncSession = Depends(get_db),
) -> DocumentRead:
    return await DocumentService.get_document(db=db, doc_id=id)


@router.patch(
    "/{id}",
    response_model=DocumentRead,
    dependencies=[Depends(require_roles("ADMIN", "QA_MANAGER", "INVESTIGATOR"))],
    summary="Update document title, description, or category",
)
async def update_document(
    id: UUID,
    payload: DocumentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DocumentRead:
    return await DocumentService.update_document(
        db=db,
        doc_id=id,
        payload=payload,
        current_user=current_user,
    )


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_roles("ADMIN"))],
    summary="Delete document (Admin only)",
)
async def delete_document(
    id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    await DocumentService.delete_document(db=db, doc_id=id, current_user=current_user)


@router.get(
    "/{id}/versions",
    response_model=List[DocumentVersionRead],
    dependencies=[Depends(require_roles("ADMIN", "QA_MANAGER", "INVESTIGATOR", "VIEWER"))],
    summary="Get all version history records for a document",
)
async def get_document_versions(
    id: UUID,
    db: AsyncSession = Depends(get_db),
) -> List[DocumentVersionRead]:
    doc = await DocumentService.get_document_or_404(db, id)
    return [DocumentVersionRead.model_validate(v) for v in doc.versions]


@router.post(
    "/{id}/versions",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles("ADMIN", "QA_MANAGER", "INVESTIGATOR"))],
    summary="Upload a new version file for an existing document",
)
async def create_new_version(
    id: UUID,
    file: UploadFile = File(...),
    change_summary: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DocumentUploadResponse:
    return await DocumentService.create_new_version(
        db=db,
        doc_id=id,
        file=file,
        change_summary=change_summary,
        current_user=current_user,
    )


@router.post(
    "/{id}/approve",
    response_model=DocumentRead,
    dependencies=[Depends(require_roles("ADMIN", "QA_MANAGER"))],
    summary="Approve document with 21 CFR Part 11 electronic signature",
)
async def approve_document(
    id: UUID,
    payload: DocumentApproval,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DocumentRead:
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    return await DocumentService.approve_document(
        db=db,
        doc_id=id,
        payload=payload,
        current_user=current_user,
        ip_address=ip_address,
        user_agent=user_agent,
    )


@router.post(
    "/{id}/archive",
    response_model=DocumentRead,
    dependencies=[Depends(require_roles("ADMIN", "QA_MANAGER"))],
    summary="Archive document",
)
async def archive_document(
    id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DocumentRead:
    return await DocumentService.archive_document(db=db, doc_id=id, current_user=current_user)


@router.post(
    "/{id}/restore",
    response_model=DocumentRead,
    dependencies=[Depends(require_roles("ADMIN", "QA_MANAGER"))],
    summary="Restore document from archive to draft",
)
async def restore_document(
    id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DocumentRead:
    return await DocumentService.restore_document(db=db, doc_id=id, current_user=current_user)


@router.get(
    "/{id}/verify",
    response_model=DocumentVerifyResponse,
    dependencies=[Depends(require_roles("ADMIN", "QA_MANAGER", "INVESTIGATOR", "VIEWER"))],
    summary="Verify cryptographic SHA-256 integrity of document file on disk",
)
async def verify_document_hash(
    id: UUID,
    version_id: Optional[UUID] = Query(None),
    db: AsyncSession = Depends(get_db),
) -> DocumentVerifyResponse:
    return await DocumentService.verify_document_hash(db=db, doc_id=id, version_id=version_id)


@router.get(
    "/{id}/download",
    dependencies=[Depends(require_roles("ADMIN", "QA_MANAGER", "INVESTIGATOR", "VIEWER"))],
    summary="Download document version file",
)
async def download_document(
    id: UUID,
    request: Request,
    version_id: Optional[UUID] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> FileResponse:


    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    storage_path, original_filename, mime_type = await DocumentService.download_document(
        db=db,
        doc_id=id,
        version_id=version_id,
        current_user=current_user,
        ip_address=ip_address,
        user_agent=user_agent,
    )

    return FileResponse(
        path=storage_path,
        filename=original_filename,
        media_type=mime_type,
    )
