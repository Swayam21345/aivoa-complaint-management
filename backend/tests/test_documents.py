"""
tests/test_documents.py
Phase 5.5 – Enterprise Document Control & Evidence Management Tests
"""

import io
import pytest
from httpx import AsyncClient


async def _create_test_complaint(client: AsyncClient) -> str:
    resp = await client.post(
        "/api/complaints",
        json={
            "product_name": "DocTest Drug 50mg",
            "batch_number": "BATCH-DOC-101",
            "customer_name": "St. Jude Hospital",
            "category": "Packaging Defect",
            "priority": "Medium",
            "risk_level": "Medium",
            "status": "UNDER_INVESTIGATION",
            "complaint_text": "Missing tamper seal.",
        },
    )
    assert resp.status_code == 201
    return resp.json()["id"]


@pytest.mark.asyncio
async def test_upload_document_and_verify_hash(
    admin_client: AsyncClient,
) -> None:
    complaint_id = await _create_test_complaint(admin_client)

    file_content = b"PDF dummy content for 21 CFR Part 11 testing"
    files = {"file": ("test_report.pdf", io.BytesIO(file_content), "application/pdf")}
    data = {
        "title": "Lab Analysis Report - Batch 101",
        "description": "Spectroscopy report for seal integrity",
        "category": "Lab Report",
        "entity_type": "COMPLAINT",
        "entity_id": complaint_id,
    }

    resp = await admin_client.post("/api/documents/upload", files=files, data=data)
    assert resp.status_code == 201, f"Upload failed: {resp.text}"
    body = resp.json()

    doc = body["document"]
    ver = body["latest_version"]

    assert doc["document_number"].startswith("DOC-")
    assert doc["title"] == "Lab Analysis Report - Batch 101"
    assert doc["status"] == "DRAFT"
    assert ver["version"] == 1
    assert ver["original_filename"] == "test_report.pdf"
    assert len(ver["sha256_hash"]) == 64

    # Verify SHA-256 integrity endpoint
    doc_id = doc["id"]
    v_res = await admin_client.get(f"/api/documents/{doc_id}/verify")
    assert v_res.status_code == 200
    v_data = v_res.json()
    assert v_data["is_valid"] is True
    assert v_data["stored_hash"] == ver["sha256_hash"]


@pytest.mark.asyncio
async def test_create_new_document_version(
    admin_client: AsyncClient,
) -> None:
    complaint_id = await _create_test_complaint(admin_client)

    # Initial Upload v1
    files1 = {"file": ("chart.png", io.BytesIO(b"PNG initial image"), "image/png")}
    data1 = {
        "title": "Seal Defect Image",
        "category": "Customer Images",
        "entity_type": "COMPLAINT",
        "entity_id": complaint_id,
    }
    up1 = await admin_client.post("/api/documents/upload", files=files1, data=data1)
    doc_id = up1.json()["document"]["id"]

    # Upload Version v2
    files2 = {"file": ("chart_hd.png", io.BytesIO(b"PNG HD updated image"), "image/png")}
    data2 = {"change_summary": "High resolution micrograph image scan added"}

    up2 = await admin_client.post(f"/api/documents/{doc_id}/versions", files=files2, data=data2)
    assert up2.status_code == 201
    body2 = up2.json()

    assert body2["document"]["current_version"] == 2
    assert body2["latest_version"]["version"] == 2
    assert body2["latest_version"]["change_summary"] == "High resolution micrograph image scan added"


@pytest.mark.asyncio
async def test_approve_document_with_signature(
    admin_client: AsyncClient,
) -> None:
    complaint_id = await _create_test_complaint(admin_client)

    files = {"file": ("cert.pdf", io.BytesIO(b"Certificate of analysis"), "application/pdf")}
    data = {
        "title": "Certificate of Analysis",
        "category": "Certificate",
        "entity_type": "COMPLAINT",
        "entity_id": complaint_id,
    }
    up = await admin_client.post("/api/documents/upload", files=files, data=data)
    doc_id = up.json()["document"]["id"]

    # Wrong password -> 401
    bad_app = await admin_client.post(
        f"/api/documents/{doc_id}/approve",
        json={"password": "WrongPassword!", "reason": "Approving CoA document."},
    )
    assert bad_app.status_code == 401

    # Valid password -> 200 APPROVED
    good_app = await admin_client.post(
        f"/api/documents/{doc_id}/approve",
        json={"password": "Admin@123", "reason": "QA Manager CoA document approval."},
    )
    assert good_app.status_code == 200
    assert good_app.json()["status"] == "APPROVED"
    assert good_app.json()["approved_by"] is not None


@pytest.mark.asyncio
async def test_archive_and_restore_document(
    admin_client: AsyncClient,
) -> None:
    complaint_id = await _create_test_complaint(admin_client)

    files = {"file": ("notes.txt", io.BytesIO(b"Investigation raw notes"), "text/plain")}
    data = {
        "title": "Raw Notes",
        "category": "Complaint Evidence",
        "entity_type": "COMPLAINT",
        "entity_id": complaint_id,
    }
    up = await admin_client.post("/api/documents/upload", files=files, data=data)
    doc_id = up.json()["document"]["id"]

    # Archive -> ARCHIVED
    arc = await admin_client.post(f"/api/documents/{doc_id}/archive")
    assert arc.status_code == 200
    assert arc.json()["status"] == "ARCHIVED"

    # Restore -> DRAFT
    res = await admin_client.post(f"/api/documents/{doc_id}/restore")
    assert res.status_code == 200
    assert res.json()["status"] == "DRAFT"


@pytest.mark.asyncio
async def test_document_download(
    admin_client: AsyncClient,
) -> None:
    complaint_id = await _create_test_complaint(admin_client)

    content_bytes = b"Sample downloadable content"
    files = {"file": ("data.csv", io.BytesIO(content_bytes), "text/csv")}
    data = {
        "title": "Lab CSV Data",
        "category": "Lab Report",
        "entity_type": "COMPLAINT",
        "entity_id": complaint_id,
    }
    up = await admin_client.post("/api/documents/upload", files=files, data=data)
    doc_id = up.json()["document"]["id"]

    dl = await admin_client.get(f"/api/documents/{doc_id}/download")
    assert dl.status_code == 200
    assert dl.content == content_bytes


@pytest.mark.asyncio
async def test_viewer_cannot_upload_or_approve(
    admin_client: AsyncClient,
    viewer_client: AsyncClient,
) -> None:
    complaint_id = await _create_test_complaint(admin_client)

    files = {"file": ("test.pdf", io.BytesIO(b"test"), "application/pdf")}
    data = {
        "title": "Viewer Upload Attempt",
        "category": "Complaint Evidence",
        "entity_type": "COMPLAINT",
        "entity_id": complaint_id,
    }

    # Upload -> 403
    up = await viewer_client.post("/api/documents/upload", files=files, data=data)
    assert up.status_code == 403


@pytest.mark.asyncio
async def test_document_dashboard_metrics(
    admin_client: AsyncClient,
) -> None:
    resp = await admin_client.get("/api/documents/dashboard")
    assert resp.status_code == 200
    data = resp.json()

    assert "total_documents" in data
    assert "approved_documents" in data
    assert "draft_documents" in data
    assert "archived_documents" in data
    assert "by_category" in data
