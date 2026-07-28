import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_and_list_suppliers(admin_client: AsyncClient) -> None:
    # Create supplier
    payload = {
        "supplier_name": "PharmaChem Global Synthetics Ltd",
        "supplier_type": "RAW_MATERIAL",
        "category": "PRIMARY",
        "risk_level": "HIGH",
        "address": "100 Innovation Parkway",
        "city": "Boston",
        "state": "MA",
        "country": "USA",
        "email": "quality@pharmachem-global.com",
    }
    res = await admin_client.post("/api/suppliers", json=payload)
    assert res.status_code == 201, res.text
    data = res.json()
    assert data["supplier_number"].startswith("SUP-")
    assert data["supplier_name"] == payload["supplier_name"]
    assert data["status"] == "PENDING_QUALIFICATION"
    sup_id = data["id"]

    # List suppliers
    list_res = await admin_client.get("/api/suppliers")
    assert list_res.status_code == 200
    assert list_res.json()["total"] >= 1


@pytest.mark.asyncio
async def test_approve_supplier_with_signature(admin_client: AsyncClient) -> None:
    # Create supplier
    res = await admin_client.post(
        "/api/suppliers",
        json={
            "supplier_name": "BioShield Packaging Corp",
            "supplier_type": "PACKAGING",
            "risk_level": "MEDIUM",
        },
    )
    sup_id = res.json()["id"]

    # Wrong password -> 401
    bad_app = await admin_client.post(
        f"/api/suppliers/{sup_id}/approve",
        json={"password": "WrongPassword!", "reason": "Supplier Qualification Approval"},
    )
    assert bad_app.status_code == 401

    # Valid password -> 200 APPROVED
    good_app = await admin_client.post(
        f"/api/suppliers/{sup_id}/approve",
        json={"password": "Admin@123", "reason": "QA Manager Qualification Approval"},
    )
    assert good_app.status_code == 200
    assert good_app.json()["status"] == "APPROVED"


@pytest.mark.asyncio
async def test_supplier_audits_and_scorecards(admin_client: AsyncClient) -> None:
    # Create supplier
    res = await admin_client.post(
        "/api/suppliers",
        json={"supplier_name": "Apex Rubber Seals Inc", "supplier_type": "COMPONENT"},
    )
    sup_id = res.json()["id"]

    # Schedule Audit
    audit_res = await admin_client.post(
        f"/api/suppliers/{sup_id}/audit",
        json={
            "audit_type": "QUALIFICATION",
            "scheduled_date": "2026-08-15T00:00:00Z",
            "auditor": "Dr. Sarah Jenkins",
        },
    )
    assert audit_res.status_code == 200
    assert audit_res.json()["audit_number"].startswith("AUD-")

    # Add Scorecard
    sc_res = await admin_client.post(
        f"/api/suppliers/{sup_id}/scorecard",
        json={
            "period": "2026-Q1",
            "quality_score": 95.0,
            "delivery_score": 90.0,
            "compliance_score": 100.0,
        },
    )
    assert sc_res.status_code == 200
    assert sc_res.json()["grade"] == "A"
    assert sc_res.json()["overall_score"] == 95.0


@pytest.mark.asyncio
async def test_supplier_nonconformance_and_corrective_action(admin_client: AsyncClient) -> None:
    # Create supplier
    res = await admin_client.post(
        "/api/suppliers",
        json={"supplier_name": "Nordic Glassware AS", "supplier_type": "RAW_MATERIAL"},
    )
    sup_id = res.json()["id"]

    # Add Nonconformance
    ncr_res = await admin_client.post(
        f"/api/suppliers/{sup_id}/nonconformance",
        json={
            "title": "Particle Contamination in Glass Vials",
            "description": "Exceeded USP <788> particulate matter thresholds.",
            "severity": "MAJOR",
        },
    )
    assert ncr_res.status_code == 200
    assert ncr_res.json()["ncr_number"].startswith("NCR-")

    # Add Corrective Action
    sca_res = await admin_client.post(
        f"/api/suppliers/{sup_id}/corrective-action",
        json={
            "action_plan": "Implement HEPA air washing before vial traying.",
            "owner": "Lars Lindqvist",
            "due_days": 30,
        },
    )
    assert sca_res.status_code == 200
    assert sca_res.json()["action_number"].startswith("SCA-")


@pytest.mark.asyncio
async def test_supplier_dashboard_and_report(admin_client: AsyncClient, viewer_client: AsyncClient) -> None:
    dash_res = await admin_client.get("/api/suppliers/dashboard")
    assert dash_res.status_code == 200
    assert "total_suppliers" in dash_res.json()

    rep_res = await admin_client.get("/api/suppliers/report")
    assert rep_res.status_code == 200
    assert "suppliers" in rep_res.json()

    # Viewer trying to view report -> 200 (read-only)
    v_dash = await viewer_client.get("/api/suppliers/dashboard")
    assert v_dash.status_code == 200
