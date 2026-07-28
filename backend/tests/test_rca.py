"""
tests/test_rca.py
Phase 5.4 – Enterprise Root Cause Analysis (RCA) & Risk Assessment (FMEA) Tests
"""

import pytest
from httpx import AsyncClient


async def _create_test_complaint(client: AsyncClient) -> str:
    """Helper to create a test complaint and return its ID."""
    resp = await client.post(
        "/api/complaints",
        json={
            "product_name": "RCA Test Drug 100mg",
            "batch_number": "BATCH-RCA-202",
            "customer_name": "Metro Pharmacy",
            "category": "Labeling Defect",
            "priority": "High",
            "risk_level": "High",
            "status": "UNDER_INVESTIGATION",
            "complaint_text": "Expirations date misprinted.",
        },
    )
    assert resp.status_code == 201
    return resp.json()["id"]


@pytest.mark.asyncio
async def test_create_rca_with_5_whys_and_fmea(
    admin_client: AsyncClient,
) -> None:
    complaint_id = await _create_test_complaint(admin_client)

    resp = await admin_client.post(
        "/api/rca",
        json={
            "complaint_id": complaint_id,
            "primary_root_cause": "Printer thermal printhead ribbon worn out causing faint text.",
            "root_cause_category": "Equipment Failure",
            "methodology": "HYBRID",
            "five_whys": [
                {"step": 1, "question": "Why was the expiry text unreadable?", "answer": "Faint ink output on carton."},
                {"step": 2, "question": "Why was the ink output faint?", "answer": "Thermal printhead heat level low."},
                {"step": 3, "question": "Why was heat level low?", "answer": "Ribbon tension roller slipped."},
                {"step": 4, "question": "Why did roller slip?", "answer": "Rubber coating degraded after 12 months."},
                {"step": 5, "question": "Why wasn't roller replaced?", "answer": "Preventive maintenance interval exceeded."},
            ],
            "fishbone": {
                "manpower": ["Operator training up to date"],
                "machine": ["Printer head roller degraded"],
                "material": ["Ink ribbon batch OK"],
                "method": ["Line check frequency insufficient"],
                "measurement": ["Visual inspect missed light prints"],
                "milieu": ["Normal room temperature"],
            },
            "fmea_items": [
                {
                    "failure_mode": "Faint expiry date print",
                    "effect_of_failure": "Patient unable to confirm shelf life safety",
                    "severity": 8,
                    "occurrence": 5,
                    "detection": 6,
                    "recommended_action": "Install inline vision camera system and replace roller every 6 months.",
                }
            ],
        },
    )
    assert resp.status_code == 201, f"Create RCA failed: {resp.text}"
    data = resp.json()

    assert data["rca_number"].startswith("RCA-")
    assert data["status"] == "DRAFT"
    assert len(data["five_whys"]) == 5
    assert len(data["fmea_items"]) == 1
    assert data["fmea_items"][0]["rpn"] == 240  # 8 * 5 * 6
    assert data["fmea_items"][0]["risk_class"] == "High"


@pytest.mark.asyncio
async def test_create_rca_viewer_forbidden(
    admin_client: AsyncClient,
    viewer_client: AsyncClient,
) -> None:
    complaint_id = await _create_test_complaint(admin_client)

    resp = await viewer_client.post(
        "/api/rca",
        json={
            "complaint_id": complaint_id,
            "primary_root_cause": "Viewer attempting RCA creation.",
        },
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_list_rcas_search_and_filter(
    admin_client: AsyncClient,
) -> None:
    complaint_id = await _create_test_complaint(admin_client)

    await admin_client.post(
        "/api/rca",
        json={
            "complaint_id": complaint_id,
            "primary_root_cause": "Equipment failure in filler valve 4.",
            "root_cause_category": "Equipment Failure",
        },
    )

    resp = await admin_client.get("/api/rca?search=filler")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 1
    assert any("filler" in item["primary_root_cause"].lower() for item in data["items"])


@pytest.mark.asyncio
async def test_approve_rca_requires_electronic_signature(
    admin_client: AsyncClient,
) -> None:
    complaint_id = await _create_test_complaint(admin_client)
    c_res = await admin_client.post(
        "/api/rca",
        json={
            "complaint_id": complaint_id,
            "primary_root_cause": "Root cause verified by engineering.",
        },
    )
    rca_id = c_res.json()["id"]

    # Wrong password -> 401
    bad_res = await admin_client.post(
        f"/api/rca/{rca_id}/approve",
        json={
            "password": "WrongPassword!",
            "reason": "Approving RCA investigation.",
        },
    )
    assert bad_res.status_code == 401

    # Valid password -> 200 APPROVED
    good_res = await admin_client.post(
        f"/api/rca/{rca_id}/approve",
        json={
            "password": "Admin@123",
            "reason": "QA Manager approving RCA after multi-factorial verification.",
        },
    )
    assert good_res.status_code == 200
    assert good_res.json()["status"] == "APPROVED"
    assert good_res.json()["approved_by"] is not None


@pytest.mark.asyncio
async def test_complaint_transition_blocked_without_approved_rca(
    admin_client: AsyncClient,
) -> None:
    complaint_id = await _create_test_complaint(admin_client)

    # Attempt to transition complaint from UNDER_INVESTIGATION -> ROOT_CAUSE_IDENTIFIED (blocked 400)
    blocked_res = await admin_client.patch(
        f"/api/complaints/{complaint_id}",
        json={"status": "ROOT_CAUSE_IDENTIFIED", "change_reason": "Attempting transition"},
    )
    assert blocked_res.status_code == 400
    assert "approved RCA record is required" in blocked_res.json()["detail"]

    # Create & approve RCA
    rca_res = await admin_client.post(
        "/api/rca",
        json={
            "complaint_id": complaint_id,
            "primary_root_cause": "Thermal head roller failure.",
        },
    )
    rca_id = rca_res.json()["id"]

    await admin_client.post(
        f"/api/rca/{rca_id}/approve",
        json={"password": "Admin@123", "reason": "Approved by QA Manager."},
    )

    # Transition now succeeds (200)
    ok_res = await admin_client.patch(
        f"/api/complaints/{complaint_id}",
        json={"status": "ROOT_CAUSE_IDENTIFIED", "change_reason": "RCA approved by QA"},
    )
    assert ok_res.status_code == 200
    assert ok_res.json()["status"] == "ROOT_CAUSE_IDENTIFIED"


@pytest.mark.asyncio
async def test_rca_dashboard_metrics(
    admin_client: AsyncClient,
) -> None:
    resp = await admin_client.get("/api/rca/dashboard")
    assert resp.status_code == 200
    data = resp.json()

    assert "total_rcas" in data
    assert "approved_rcas" in data
    assert "high_risk_fmea_count" in data
    assert "average_rpn" in data
    assert "by_category" in data
