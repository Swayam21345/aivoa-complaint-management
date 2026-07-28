import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_and_get_complaint_with_history(
    async_client: AsyncClient,
) -> None:
    # Create complaint
    create_payload = {
        "product_name": "Atorvastatin 20mg",
        "batch_number": "AT-2026-101",
        "customer_name": "Apex Pharma Distributors",
        "category": "Packaging Defect",
        "risk_level": "High",
        "priority": "Critical",
        "status": "NEW",
        "complaint_text": "Blister seal compromised leading to tablet degradation.",
        "submitted_by": "QA Auditor",
    }
    res = await async_client.post("/api/complaints", json=create_payload)
    assert res.status_code == 201
    data = res.json()
    complaint_uuid = data["id"]
    assert data["status"] == "NEW"

    # Get complaint detail
    detail_res = await async_client.get(f"/api/complaints/{complaint_uuid}")
    assert detail_res.status_code == 200
    detail = detail_res.json()
    assert detail["product_name"] == "Atorvastatin 20mg"
    assert detail["priority"] == "Critical"
    assert len(detail["history"]) == 1
    assert detail["history"][0]["new_status"] == "NEW"
    assert detail["history"][0]["old_status"] is None


@pytest.mark.asyncio
async def test_status_workflow_transitions_log_history(
    async_client: AsyncClient,
) -> None:
    # Create complaint
    res = await async_client.post(
        "/api/complaints",
        json={
            "product_name": "Metformin 500mg",
            "customer_name": "City Health Hospital",
            "status": "NEW",
        },
    )
    complaint_uuid = res.json()["id"]

    # Transition to UNDER_REVIEW
    patch1 = await async_client.patch(
        f"/api/complaints/{complaint_uuid}",
        json={
            "status": "UNDER_REVIEW",
            "changed_by": "Lead Investigator",
            "change_reason": "Triage investigation started",
        },
    )
    assert patch1.status_code == 200
    assert patch1.json()["status"] == "UNDER_REVIEW"

    # Transition to IN_PROGRESS
    patch2 = await async_client.patch(
        f"/api/complaints/{complaint_uuid}",
        json={
            "status": "IN_PROGRESS",
            "changed_by": "Lab Technician",
            "change_reason": "Root cause lab testing underway",
        },
    )
    assert patch2.status_code == 200

    # Transition to RESOLVED
    patch3 = await async_client.patch(
        f"/api/complaints/{complaint_uuid}",
        json={
            "status": "RESOLVED",
            "changed_by": "QA Director",
            "change_reason": "CAPA action plan executed",
        },
    )
    assert patch3.status_code == 200

    # Check detail history audit log
    detail_res = await async_client.get(f"/api/complaints/{complaint_uuid}")
    detail = detail_res.json()
    assert len(detail["history"]) == 4
    statuses = [h["new_status"] for h in detail["history"]]
    assert statuses == ["NEW", "UNDER_REVIEW", "IN_PROGRESS", "RESOLVED"]


@pytest.mark.asyncio
async def test_search_and_filtering(async_client: AsyncClient) -> None:
    # Seed test data
    c1 = {
        "product_name": "Amoxicillin 250mg",
        "customer_name": "Metropolitan Clinic",
        "category": "Foreign Material",
        "priority": "High",
        "risk_level": "High",
        "status": "NEW",
        "complaint_text": "Particulate matter observed inside vial.",
    }
    c2 = {
        "product_name": "Lisinopril 10mg",
        "customer_name": "Sunrise Pharmacy",
        "category": "Labeling Error",
        "priority": "Low",
        "risk_level": "Low",
        "status": "CLOSED",
        "complaint_text": "Expiry date printed faintly on outer box.",
    }
    await async_client.post("/api/complaints", json=c1)
    await async_client.post("/api/complaints", json=c2)

    # Filter by priority=High
    res_priority = await async_client.get("/api/complaints?priority=High")
    assert res_priority.status_code == 200
    data_p = res_priority.json()
    assert data_p["total"] == 1
    assert data_p["items"][0]["product_name"] == "Amoxicillin 250mg"

    # Search by partial text 'vial'
    res_search = await async_client.get("/api/complaints?search=vial")
    assert res_search.status_code == 200
    data_s = res_search.json()
    assert data_s["total"] == 1
    assert data_s["items"][0]["product_name"] == "Amoxicillin 250mg"

    # Filter by status=CLOSED
    res_status = await async_client.get("/api/complaints?status=CLOSED")
    assert res_status.status_code == 200
    assert res_status.json()["total"] == 1


@pytest.mark.asyncio
async def test_reviewer_notes_crud_and_soft_delete(
    async_client: AsyncClient,
) -> None:
    # Create complaint
    res = await async_client.post(
        "/api/complaints",
        json={"product_name": "Omeprazole 20mg", "status": "NEW"},
    )
    complaint_uuid = res.json()["id"]

    # Add reviewer note
    note_res = await async_client.post(
        f"/api/complaints/{complaint_uuid}/notes",
        json={
            "author": "Dr. Smith",
            "content": "Initial sample requested for lab analysis.",
        },
    )
    assert note_res.status_code == 201
    note_data = note_res.json()
    note_uuid = note_data["id"]
    assert note_data["author"] == "Dr. Smith"

    # List notes
    list_notes_res = await async_client.get(
        f"/api/complaints/{complaint_uuid}/notes"
    )
    assert list_notes_res.status_code == 200
    assert len(list_notes_res.json()) == 1

    # Update note
    update_note_res = await async_client.patch(
        f"/api/complaints/{complaint_uuid}/notes/{note_uuid}",
        json={"content": "Updated: Lab sample received and under assay."},
    )
    assert update_note_res.status_code == 200
    assert "Lab sample received" in update_note_res.json()["content"]

    # Delete note
    del_note_res = await async_client.delete(
        f"/api/complaints/{complaint_uuid}/notes/{note_uuid}"
    )
    assert del_note_res.status_code == 204

    # Verify note list is empty
    list_after_del = await async_client.get(
        f"/api/complaints/{complaint_uuid}/notes"
    )
    assert len(list_after_del.json()) == 0

    # Soft delete complaint
    del_complaint_res = await async_client.delete(
        f"/api/complaints/{complaint_uuid}"
    )
    assert del_complaint_res.status_code == 204

    # Verify complaint detail returns 404
    get_404 = await async_client.get(f"/api/complaints/{complaint_uuid}")
    assert get_404.status_code == 404
