import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_and_list_internal_audits(admin_client: AsyncClient) -> None:
    # Create internal audit
    payload = {
        "title": "Annual 21 CFR Part 820 & ISO 13485 Internal Quality System Audit",
        "audit_type": "INTERNAL_SOP",
        "scope": "Comprehensive evaluation of Quality Assurance, CAPA, and Complaint Handling.",
        "lead_auditor": "Dr. Aris Thorne",
        "audit_team": "Elena Vance, Marcus Brody",
        "department": "QUALITY_ASSURANCE",
        "scheduled_start_date": "2026-09-01T09:00:00Z",
        "scheduled_end_date": "2026-09-05T17:00:00Z",
    }
    res = await admin_client.post("/api/internal-audits", json=payload)
    assert res.status_code == 201, res.text
    data = res.json()
    assert data["audit_number"].startswith("IAU-")
    assert data["status"] == "PLANNED"
    audit_id = data["id"]

    # List internal audits
    list_res = await admin_client.get("/api/internal-audits")
    assert list_res.status_code == 200
    assert list_res.json()["total"] >= 1


@pytest.mark.asyncio
async def test_checklist_and_findings_logging(admin_client: AsyncClient) -> None:
    # Create audit
    res = await admin_client.post(
        "/api/internal-audits",
        json={
            "title": "Cleanroom Environmental Monitoring Audit",
            "scope": "Evaluate ISO Class 5 and Class 7 cleanrooms.",
            "lead_auditor": "Sarah Connor",
            "scheduled_start_date": "2026-10-01T09:00:00Z",
            "scheduled_end_date": "2026-10-02T17:00:00Z",
        },
    )
    audit_id = res.json()["id"]

    # Add Checklist
    chk_res = await admin_client.post(
        f"/api/internal-audits/{audit_id}/checklist",
        json={
            "section": "Section 4.2",
            "requirement": "Differential Pressure Logs",
            "question": "Are differential pressures recorded every shift?",
            "compliance_status": "COMPLIANT",
            "comments": "All shift logbooks verified compliant.",
        },
    )
    assert chk_res.status_code == 200

    # Add Finding
    find_res = await admin_client.post(
        f"/api/internal-audits/{audit_id}/finding",
        json={
            "category": "MAJOR_NC",
            "description": "HEPA filter integrity testing overdue by 14 days in Bay 3.",
            "clause_reference": "ISO 13485:2016 Cl. 6.4",
        },
    )
    assert find_res.status_code == 200
    assert find_res.json()["finding_number"].startswith("AFN-")


@pytest.mark.asyncio
async def test_approve_and_close_audit_with_signature(admin_client: AsyncClient) -> None:
    # Create audit
    res = await admin_client.post(
        "/api/internal-audits",
        json={
            "title": "Software Validation Audit",
            "scope": "Computer Systems Validation per GAMP 5",
            "lead_auditor": "David Miller",
            "scheduled_start_date": "2026-11-01T09:00:00Z",
            "scheduled_end_date": "2026-11-02T17:00:00Z",
        },
    )
    audit_id = res.json()["id"]

    # Wrong password -> 401
    bad_app = await admin_client.post(
        f"/api/internal-audits/{audit_id}/approve",
        json={"password": "WrongPassword!", "reason": "Internal Audit Report Closure"},
    )
    assert bad_app.status_code == 401

    # Valid password -> 200 CLOSED
    good_app = await admin_client.post(
        f"/api/internal-audits/{audit_id}/approve",
        json={
            "password": "Admin@123",
            "reason": "QA Manager Audit Report Signoff",
            "conclusion": "Audit completed. All findings remediated.",
        },
    )
    assert good_app.status_code == 200
    assert good_app.json()["status"] == "CLOSED"


@pytest.mark.asyncio
async def test_inspection_readiness_packages(admin_client: AsyncClient) -> None:
    # Create Readiness Package
    pkg_res = await admin_client.post(
        "/api/internal-audits/readiness-packages",
        json={
            "agency": "FDA",
            "title": "FDA QSIT Inspection Readiness Package 2026",
            "description": "Pre-compiled dossier covering Management Controls, CAPA, and Design Controls.",
            "readiness_score": 98.5,
        },
    )
    assert pkg_res.status_code == 201
    assert pkg_res.json()["package_number"].startswith("IRP-")

    # List packages
    list_res = await admin_client.get("/api/internal-audits/readiness-packages")
    assert list_res.status_code == 200
    assert len(list_res.json()) >= 1


@pytest.mark.asyncio
async def test_internal_audit_dashboard(admin_client: AsyncClient, viewer_client: AsyncClient) -> None:
    dash_res = await admin_client.get("/api/internal-audits/dashboard")
    assert dash_res.status_code == 200
    data = dash_res.json()
    assert "total_audits" in data
    assert "avg_inspection_readiness_score" in data

    # Viewer client read access -> 200
    v_res = await viewer_client.get("/api/internal-audits/dashboard")
    assert v_res.status_code == 200
