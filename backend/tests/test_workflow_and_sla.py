import pytest
from fastapi import HTTPException
from httpx import AsyncClient

from app.services.workflow_service import validate_status_transition_for_role


@pytest.mark.asyncio
async def test_status_workflow_transitions():
    # 1. Valid Admin workflow transitions
    validate_status_transition_for_role("ADMIN", "NEW", "TRIAGED")
    validate_status_transition_for_role("ADMIN", "TRIAGED", "ASSIGNED")
    validate_status_transition_for_role("ADMIN", "ASSIGNED", "UNDER_INVESTIGATION")
    validate_status_transition_for_role("ADMIN", "UNDER_INVESTIGATION", "ROOT_CAUSE_IDENTIFIED")
    validate_status_transition_for_role("ADMIN", "ROOT_CAUSE_IDENTIFIED", "CAPA_IN_PROGRESS")
    validate_status_transition_for_role("ADMIN", "CAPA_IN_PROGRESS", "QA_REVIEW")
    validate_status_transition_for_role("ADMIN", "QA_REVIEW", "QA_APPROVED")
    validate_status_transition_for_role("ADMIN", "QA_APPROVED", "CLOSED")

    # 2. Invalid state machine transition -> HTTP 400
    with pytest.raises(HTTPException) as exc1:
        validate_status_transition_for_role("ADMIN", "NEW", "CLOSED")
    assert exc1.value.status_code == 400

    # 3. Role-based transition authorization check -> HTTP 403
    # Investigator attempting QA Approval -> 403
    with pytest.raises(HTTPException) as exc2:
        validate_status_transition_for_role("INVESTIGATOR", "QA_REVIEW", "QA_APPROVED")
    assert exc2.value.status_code == 403

    # Viewer attempting any status change -> 403
    with pytest.raises(HTTPException) as exc3:
        validate_status_transition_for_role("VIEWER", "NEW", "TRIAGED")
    assert exc3.value.status_code == 403


@pytest.mark.asyncio
async def test_complaint_assignment_rbac(
    admin_client: AsyncClient,
    viewer_client: AsyncClient,
    investigator_client: AsyncClient,
):
    # 1. Create complaint as admin
    create_resp = await admin_client.post(
        "/api/complaints",
        json={
            "product_name": "Test Antibiotic 500mg",
            "batch_number": "BATCH-SLA-101",
            "customer_name": "St. Jude Hospital",
            "category": "Product Quality Defect",
            "priority": "Critical",
            "risk_level": "High",
            "status": "NEW",
            "complaint_text": "Sample vial broken upon arrival.",
        },
    )
    assert create_resp.status_code == 201
    c_data = create_resp.json()
    complaint_id = c_data["id"]

    # 2. Assign investigator as Admin -> Should succeed
    assign_resp = await admin_client.post(
        f"/api/complaints/{complaint_id}/assign",
        json={"assigned_to": "Lead Investigator"},
    )
    assert assign_resp.status_code == 200
    detail = assign_resp.json()
    assert detail["assigned_to"] == "Lead Investigator"
    assert detail["assigned_by"] is not None

    # 3. Viewer attempts to assign -> Should return 403 Forbidden
    viewer_assign = await viewer_client.post(
        f"/api/complaints/{complaint_id}/assign",
        json={"assigned_to": "Unauthorized User"},
    )
    assert viewer_assign.status_code == 403

    # 4. Fetch activity feed
    act_resp = await admin_client.get(f"/api/complaints/{complaint_id}/activity")
    assert act_resp.status_code == 200
    activity = act_resp.json()
    assert any(a["action_type"] == "Assigned" for a in activity)


@pytest.mark.asyncio
async def test_investigator_dashboard(admin_client: AsyncClient):
    resp = await admin_client.get("/api/dashboard/investigator")
    assert resp.status_code == 200
    data = resp.json()
    assert "assigned_to_me" in data
    assert "pending_reviews" in data
    assert "overdue_cases" in data
    assert "completed_this_month" in data
    assert "average_resolution_time" in data
