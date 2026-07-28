import pytest
from httpx import AsyncClient

from app.schemas.complaint import ComplaintCreate


@pytest.mark.asyncio
async def test_copilot_timeline_export_endpoints(async_client: AsyncClient) -> None:
    # 1. Create a complaint first
    create_payload: dict = {
        "product_name": "Ibuprofen 400mg",
        "batch_number": "BATCH-2026-X1",
        "customer_name": "St. Jude Hospital",
        "category": "Product Quality Defect",
        "risk_level": "High",
        "priority": "Critical",
        "complaint_text": "Chipped tablets observed in blister strip.",
    }
    res = await async_client.post("/api/complaints", json=create_payload)
    assert res.status_code == 201
    created_data = res.json()
    complaint_id = created_data["id"]

    # 2. Test GET /api/complaints/{id}/copilot
    copilot_res = await async_client.get(f"/api/complaints/{complaint_id}/copilot")
    assert copilot_res.status_code == 200
    copilot_data = copilot_res.json()
    assert "complaint_summary" in copilot_data
    assert "confidence_scores" in copilot_data

    # 3. Test GET /api/complaints/{id}/timeline
    timeline_res = await async_client.get(f"/api/complaints/{complaint_id}/timeline")
    assert timeline_res.status_code == 200
    timeline_data = timeline_res.json()
    assert "events" in timeline_data
    assert len(timeline_data["events"]) >= 1
    assert timeline_data["events"][0]["event_type"] == "CREATED"

    # 4. Test GET /api/complaints/{id}/export/pdf
    pdf_res = await async_client.get(f"/api/complaints/{complaint_id}/export/pdf")
    assert pdf_res.status_code == 200
    assert pdf_res.headers["content-type"] == "application/pdf"
    assert pdf_res.content.startswith(b"%PDF")
