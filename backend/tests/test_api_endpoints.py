import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_full_complaint_workflow(async_client: AsyncClient) -> None:
    # 1. Ingest document via POST /api/upload
    upload_resp = await async_client.post(
        "/api/upload",
        data={
            "input_type": "text",
            "text": "Leaking bottle for Ibuprofen 400mg, Lot #IBU-2026-88.",
        },
    )
    assert upload_resp.status_code == 200
    upload_data = upload_resp.json()
    assert upload_data["status"] == "success"
    assert "extracted_text" in upload_data
    assert upload_data["ai_analysis"] is not None

    ai = upload_data["ai_analysis"]

    # 2. Create complaint via POST /api/complaints
    create_payload = {
        "product_name": "Ibuprofen 400mg",
        "batch_number": "IBU-2026-88",
        "customer_name": "MediHealth Clinic",
        "category": ai.get("category") or "Product Quality Defect",
        "risk_level": ai.get("risk_level") or "Medium",
        "complaint_text": upload_data["extracted_text"],
        "reviewer_notes": "Initial triage note",
        "submitted_by": "QA Engineer",
        "ai_analysis": ai,
    }

    create_resp = await async_client.post("/api/complaints", json=create_payload)
    assert create_resp.status_code == 201
    create_data = create_resp.json()
    assert "complaint_id" in create_data
    assert create_data["status"] in ("Draft", "NEW")
    complaint_uuid = create_data["id"]

    # 3. List complaints via GET /api/complaints
    list_resp = await async_client.get("/api/complaints")
    assert list_resp.status_code == 200
    list_data = list_resp.json()
    assert list_data["total"] == 1
    assert list_data["items"][0]["id"] == complaint_uuid

    # 4. Get complaint detail via GET /api/complaints/{id}
    detail_resp = await async_client.get(f"/api/complaints/{complaint_uuid}")
    assert detail_resp.status_code == 200
    detail_data = detail_resp.json()
    assert detail_data["product_name"] == "Ibuprofen 400mg"
    assert detail_data["ai_analysis"] is not None

    # 5. Patch complaint status via PATCH /api/complaints/{id}
    patch_payload = {
        "status": "UNDER_REVIEW",
        "reviewer_notes": "Assigned to Lead Investigator.",
    }
    patch_resp = await async_client.patch(
        f"/api/complaints/{complaint_uuid}", json=patch_payload
    )
    assert patch_resp.status_code == 200
    patch_data = patch_resp.json()
    assert patch_data["status"] == "UNDER_REVIEW"
