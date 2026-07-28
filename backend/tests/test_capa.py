"""
tests/test_capa.py
Phase 5.3 – Enterprise CAPA (Corrective and Preventive Action) Management Tests
"""

import pytest
from httpx import AsyncClient


async def _create_test_complaint(client: AsyncClient) -> str:
    """Helper to create a test complaint and return its ID."""
    resp = await client.post(
        "/api/complaints",
        json={
            "product_name": "CAPA Test Drug 50mg",
            "batch_number": "BATCH-CAPA-101",
            "customer_name": "Apex Hospital",
            "category": "Packaging Defect",
            "priority": "High",
            "risk_level": "High",
            "status": "ROOT_CAUSE_IDENTIFIED",
            "complaint_text": "Blister pack unsealed.",
        },
    )
    assert resp.status_code == 201
    return resp.json()["id"]


@pytest.mark.asyncio
async def test_create_capa_success(
    admin_client: AsyncClient,
) -> None:
    complaint_id = await _create_test_complaint(admin_client)

    resp = await admin_client.post(
        "/api/capa",
        json={
            "complaint_id": complaint_id,
            "title": "Seal Integrity Line Calibration",
            "description": "Recalibrate sealing temperature sensor on Line 3.",
            "root_cause": "Temperature sensor drift over 6 months.",
            "corrective_action": "Quarantine affected lot and replace sensor.",
            "preventive_action": "Implement monthly sensor calibration schedule.",
            "owner": "Dr. Sarah Connor",
            "priority": "High",
            "risk_level": "High",
        },
    )
    assert resp.status_code == 201, f"Create CAPA failed: {resp.text}"
    data = resp.json()

    assert data["capa_number"].startswith("CAPA-")
    assert data["title"] == "Seal Integrity Line Calibration"
    assert data["status"] == "OPEN"
    assert data["owner"] == "Dr. Sarah Connor"


@pytest.mark.asyncio
async def test_create_capa_viewer_forbidden(
    admin_client: AsyncClient,
    viewer_client: AsyncClient,
) -> None:
    complaint_id = await _create_test_complaint(admin_client)

    resp = await viewer_client.post(
        "/api/capa",
        json={
            "complaint_id": complaint_id,
            "title": "Unauthorized CAPA Creation",
            "description": "Viewer attempting to create CAPA.",
        },
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_list_capas_pagination_and_search(
    admin_client: AsyncClient,
) -> None:
    complaint_id = await _create_test_complaint(admin_client)

    # Create 2 CAPAs
    await admin_client.post(
        "/api/capa",
        json={
            "complaint_id": complaint_id,
            "title": "Filter Test Alpha",
            "description": "Alpha description text.",
        },
    )
    await admin_client.post(
        "/api/capa",
        json={
            "complaint_id": complaint_id,
            "title": "Filter Test Beta",
            "description": "Beta description text.",
        },
    )

    resp = await admin_client.get("/api/capa?search=Alpha")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 1
    assert any("Alpha" in item["title"] for item in data["items"])


@pytest.mark.asyncio
async def test_capa_detail_endpoint(
    admin_client: AsyncClient,
) -> None:
    complaint_id = await _create_test_complaint(admin_client)
    create_res = await admin_client.post(
        "/api/capa",
        json={
            "complaint_id": complaint_id,
            "title": "Detail Fetch Test",
            "description": "Checking GET by ID.",
        },
    )
    capa_id = create_res.json()["id"]

    resp = await admin_client.get(f"/api/capa/{capa_id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == capa_id


@pytest.mark.asyncio
async def test_update_capa_fields_and_status(
    admin_client: AsyncClient,
) -> None:
    complaint_id = await _create_test_complaint(admin_client)
    create_res = await admin_client.post(
        "/api/capa",
        json={
            "complaint_id": complaint_id,
            "title": "Status Transition Test",
            "description": "Initial state OPEN.",
        },
    )
    capa_id = create_res.json()["id"]

    # Transition to UNDER_IMPLEMENTATION
    update_res = await admin_client.patch(
        f"/api/capa/{capa_id}",
        json={"status": "UNDER_IMPLEMENTATION", "owner": "John Doe"},
    )
    assert update_res.status_code == 200
    assert update_res.json()["status"] == "UNDER_IMPLEMENTATION"
    assert update_res.json()["owner"] == "John Doe"


@pytest.mark.asyncio
async def test_delete_capa_permissions(
    admin_client: AsyncClient,
    investigator_client: AsyncClient,
) -> None:
    complaint_id = await _create_test_complaint(admin_client)
    create_res = await admin_client.post(
        "/api/capa",
        json={
            "complaint_id": complaint_id,
            "title": "Deletion Test",
            "description": "To be deleted.",
        },
    )
    capa_id = create_res.json()["id"]

    # Investigator cannot delete
    del_inv = await investigator_client.delete(f"/api/capa/{capa_id}")
    assert del_inv.status_code == 403

    # Admin can delete
    del_adm = await admin_client.delete(f"/api/capa/{capa_id}")
    assert del_adm.status_code == 204



@pytest.mark.asyncio
async def test_effectiveness_review_requires_signature(
    admin_client: AsyncClient,
) -> None:
    complaint_id = await _create_test_complaint(admin_client)
    c_res = await admin_client.post(
        "/api/capa",
        json={
            "complaint_id": complaint_id,
            "title": "Effectiveness Review Test",
            "description": "Checking 21 CFR Part 11 effectiveness review.",
        },
    )
    capa_id = c_res.json()["id"]

    # Transition OPEN -> UNDER_IMPLEMENTATION -> PENDING_EFFECTIVENESS
    await admin_client.patch(f"/api/capa/{capa_id}", json={"status": "UNDER_IMPLEMENTATION"})
    await admin_client.patch(f"/api/capa/{capa_id}", json={"status": "PENDING_EFFECTIVENESS"})


    # Wrong password fails 401
    bad_res = await admin_client.post(
        f"/api/capa/{capa_id}/effectiveness",
        json={
            "password": "WrongPassword!",
            "effectiveness_check": "Verified zero reoccurrences on Line 3.",
            "is_effective": True,
            "reason": "Effectiveness check approved by QA.",
        },
    )
    assert bad_res.status_code == 401

    # Valid signature passes 200 -> EFFECTIVE
    good_res = await admin_client.post(
        f"/api/capa/{capa_id}/effectiveness",
        json={
            "password": "Admin@123",
            "effectiveness_check": "Verified zero reoccurrences on Line 3.",
            "is_effective": True,
            "reason": "Effectiveness check approved by QA after 30 days monitoring.",
        },
    )
    assert good_res.status_code == 200
    assert good_res.json()["status"] == "EFFECTIVE"


@pytest.mark.asyncio
async def test_close_capa_with_signature(
    admin_client: AsyncClient,
) -> None:
    complaint_id = await _create_test_complaint(admin_client)
    c_res = await admin_client.post(
        "/api/capa",
        json={
            "complaint_id": complaint_id,
            "title": "Closure Signature Test",
            "description": "Testing CAPA closure e-signature.",
        },
    )
    capa_id = c_res.json()["id"]

    close_res = await admin_client.post(
        f"/api/capa/{capa_id}/close",
        json={
            "password": "Admin@123",
            "reason": "Closing CAPA after complete implementation and validation.",
        },
    )
    assert close_res.status_code == 200
    assert close_res.json()["status"] == "CLOSED"


@pytest.mark.asyncio
async def test_complaint_qa_approval_blocked_by_open_capa(
    admin_client: AsyncClient,
) -> None:
    complaint_id = await _create_test_complaint(admin_client)

    # Advance complaint to QA_REVIEW
    transitions = [
        ("ROOT_CAUSE_IDENTIFIED", "CAPA_IN_PROGRESS"),
        ("CAPA_IN_PROGRESS", "QA_REVIEW"),
    ]
    for from_s, to_s in transitions:
        r = await admin_client.patch(
            f"/api/complaints/{complaint_id}",
            json={"status": to_s, "change_reason": f"Advancing to {to_s}"},
        )
        assert r.status_code == 200

    # Create an OPEN CAPA for this complaint
    capa_res = await admin_client.post(
        "/api/capa",
        json={
            "complaint_id": complaint_id,
            "title": "Blocking CAPA",
            "description": "This CAPA must be closed before complaint QA approval.",
        },
    )
    capa_id = capa_res.json()["id"]

    # Attempt to sign/approve complaint -> Should be BLOCKED (400)
    app_res = await admin_client.post(
        f"/api/complaints/{complaint_id}/sign",
        json={
            "password": "Admin@123",
            "reason": "Trying to approve with open CAPAs.",
            "target_status": "QA_APPROVED",
        },
    )
    assert app_res.status_code == 400
    assert "associated CAPAs must be CLOSED" in app_res.json()["detail"]

    # Now close the CAPA
    await admin_client.post(
        f"/api/capa/{capa_id}/close",
        json={
            "password": "Admin@123",
            "reason": "Closing CAPA so complaint can be approved.",
        },
    )

    # Attempt to sign/approve complaint again -> Should SUCCEED (200)
    app_res2 = await admin_client.post(
        f"/api/complaints/{complaint_id}/sign",
        json={
            "password": "Admin@123",
            "reason": "All CAPAs closed. Approving complaint QA.",
            "target_status": "QA_APPROVED",
        },
    )
    assert app_res2.status_code == 200
    assert app_res2.json()["signed"] is True


@pytest.mark.asyncio
async def test_capa_dashboard_metrics(
    admin_client: AsyncClient,
) -> None:
    resp = await admin_client.get("/api/capa/dashboard")
    assert resp.status_code == 200
    data = resp.json()

    assert "open_capas" in data
    assert "overdue_capas" in data
    assert "pending_effectiveness" in data
    assert "closed_this_month" in data
    assert "monthly_trends" in data
