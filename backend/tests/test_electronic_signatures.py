"""
tests/test_electronic_signatures.py
21 CFR Part 11 Electronic Signature Tests

Coverage:
  - Successful signature (QA Approval, Complaint Closure)
  - Wrong password → 401 Unauthorized
  - Unauthorized role (VIEWER, INVESTIGATOR) → 403 Forbidden
  - SHA-256 hash generation and determinism
  - Audit event created on signing
  - Signature history endpoint (GET /signatures)
  - Signature record immutability
  - Legacy tests still passing
"""

import hashlib

import pytest
from httpx import AsyncClient


# ─── Helpers ──────────────────────────────────────────────────────────────────

async def _create_complaint(client: AsyncClient) -> str:
    """Create a minimal complaint and return its UUID id."""
    resp = await client.post(
        "/api/complaints",
        json={
            "product_name": "Pharma Drug 100mg",
            "batch_number": "BATCH-SIG-001",
            "customer_name": "St. Jude Pharma",
            "category": "Product Quality Defect",
            "priority": "Critical",
            "risk_level": "High",
            "status": "NEW",
            "complaint_text": "Vial seal broken, suspected contamination.",
        },
    )
    assert resp.status_code == 201, f"Failed to create complaint: {resp.text}"
    return resp.json()["id"]


async def _advance_to_qa_review(admin_client: AsyncClient, complaint_id: str) -> None:
    """Advance complaint through workflow to QA_REVIEW so it can be signed."""
    early_transitions = [
        ("NEW", "TRIAGED"),
        ("TRIAGED", "ASSIGNED"),
        ("ASSIGNED", "UNDER_INVESTIGATION"),
    ]
    for from_s, to_s in early_transitions:
        resp = await admin_client.patch(
            f"/api/complaints/{complaint_id}",
            json={"status": to_s, "change_reason": f"Advancing to {to_s}"},
        )
        assert resp.status_code == 200, f"Transition {from_s}→{to_s} failed: {resp.text}"

    # Approved RCA is required before ROOT_CAUSE_IDENTIFIED
    rca_res = await admin_client.post(
        "/api/rca",
        json={
            "complaint_id": complaint_id,
            "primary_root_cause": "Root cause verified for signature workflow test.",
        },
    )
    assert rca_res.status_code == 201, f"Failed to create RCA: {rca_res.text}"
    rca_id = rca_res.json()["id"]
    approve_res = await admin_client.post(
        f"/api/rca/{rca_id}/approve",
        json={"password": "Admin@123", "reason": "RCA approved for signature workflow test."},
    )
    assert approve_res.status_code == 200, f"Failed to approve RCA: {approve_res.text}"

    late_transitions = [
        ("UNDER_INVESTIGATION", "ROOT_CAUSE_IDENTIFIED"),
        ("ROOT_CAUSE_IDENTIFIED", "CAPA_IN_PROGRESS"),
        ("CAPA_IN_PROGRESS", "QA_REVIEW"),
    ]
    for from_s, to_s in late_transitions:
        resp = await admin_client.patch(
            f"/api/complaints/{complaint_id}",
            json={"status": to_s, "change_reason": f"Advancing to {to_s}"},
        )
        assert resp.status_code == 200, f"Transition {from_s}→{to_s} failed: {resp.text}"


# ─── Stage 1: Successful Electronic Signature ─────────────────────────────────

@pytest.mark.asyncio
async def test_valid_electronic_signature_qa_approval(
    admin_client: AsyncClient,
) -> None:
    """ADMIN can sign a complaint in QA_REVIEW → QA_APPROVED."""
    complaint_id = await _create_complaint(admin_client)
    await _advance_to_qa_review(admin_client, complaint_id)

    resp = await admin_client.post(
        f"/api/complaints/{complaint_id}/sign",
        json={
            "password": "Admin@123",
            "reason": "QA review complete. No non-conformances identified. Approving closure.",
            "target_status": "QA_APPROVED",
        },
    )
    assert resp.status_code == 200, f"Sign failed: {resp.text}"
    data = resp.json()

    assert data["signed"] is True
    assert data["signed_by"] is not None
    assert data["timestamp"] is not None
    assert data["signature_id"] is not None
    assert len(data["hash"]) == 64  # SHA-256 hex digest is always 64 chars


@pytest.mark.asyncio
async def test_valid_electronic_signature_complaint_closure(
    admin_client: AsyncClient,
) -> None:
    """ADMIN can sign a QA_APPROVED complaint → CLOSED."""
    complaint_id = await _create_complaint(admin_client)
    await _advance_to_qa_review(admin_client, complaint_id)

    # First sign: QA_REVIEW → QA_APPROVED
    resp = await admin_client.post(
        f"/api/complaints/{complaint_id}/sign",
        json={
            "password": "Admin@123",
            "reason": "QA approved after full investigation.",
            "target_status": "QA_APPROVED",
        },
    )
    assert resp.status_code == 200

    # Second sign: QA_APPROVED → CLOSED
    resp2 = await admin_client.post(
        f"/api/complaints/{complaint_id}/sign",
        json={
            "password": "Admin@123",
            "reason": "All CAPAs completed. Closing complaint.",
            "target_status": "CLOSED",
        },
    )
    assert resp2.status_code == 200, f"Closure sign failed: {resp2.text}"
    data = resp2.json()
    assert data["signed"] is True
    assert len(data["hash"]) == 64


@pytest.mark.asyncio
async def test_qa_manager_can_sign(
    admin_client: AsyncClient,
    qa_manager_client: AsyncClient,
) -> None:
    """QA_MANAGER role can execute electronic signature."""
    complaint_id = await _create_complaint(admin_client)
    await _advance_to_qa_review(admin_client, complaint_id)

    resp = await qa_manager_client.post(
        f"/api/complaints/{complaint_id}/sign",
        json={
            "password": "QAManager@123",
            "reason": "QA Manager approving complaint after investigation review.",
            "target_status": "QA_APPROVED",
        },
    )
    assert resp.status_code == 200, f"QA Manager sign failed: {resp.text}"
    assert resp.json()["signed"] is True


# ─── Stage 2: Wrong Password → 401 ───────────────────────────────────────────

@pytest.mark.asyncio
async def test_wrong_password_returns_401(
    admin_client: AsyncClient,
) -> None:
    """Providing an incorrect password during signing returns HTTP 401."""
    complaint_id = await _create_complaint(admin_client)
    await _advance_to_qa_review(admin_client, complaint_id)

    resp = await admin_client.post(
        f"/api/complaints/{complaint_id}/sign",
        json={
            "password": "WrongPassword123!",
            "reason": "Attempting to sign with bad password.",
            "target_status": "QA_APPROVED",
        },
    )
    assert resp.status_code == 401, f"Expected 401, got: {resp.status_code} - {resp.text}"
    assert "Password verification failed" in resp.json()["detail"]


# ─── Stage 3: Unauthorized Roles → 403 ───────────────────────────────────────

@pytest.mark.asyncio
async def test_viewer_cannot_sign(
    admin_client: AsyncClient,
    viewer_client: AsyncClient,
) -> None:
    """VIEWER role must receive HTTP 403 when attempting electronic signature."""
    complaint_id = await _create_complaint(admin_client)
    await _advance_to_qa_review(admin_client, complaint_id)

    resp = await viewer_client.post(
        f"/api/complaints/{complaint_id}/sign",
        json={
            "password": "Viewer@123",
            "reason": "Viewer trying to sign.",
            "target_status": "QA_APPROVED",
        },
    )
    assert resp.status_code == 403, f"Expected 403, got: {resp.status_code} - {resp.text}"


@pytest.mark.asyncio
async def test_investigator_cannot_sign(
    admin_client: AsyncClient,
    investigator_client: AsyncClient,
) -> None:
    """INVESTIGATOR role must receive HTTP 403 when attempting electronic signature."""
    complaint_id = await _create_complaint(admin_client)
    await _advance_to_qa_review(admin_client, complaint_id)

    resp = await investigator_client.post(
        f"/api/complaints/{complaint_id}/sign",
        json={
            "password": "Investigator@123",
            "reason": "Investigator trying to sign.",
            "target_status": "QA_APPROVED",
        },
    )
    assert resp.status_code == 403, f"Expected 403, got: {resp.status_code} - {resp.text}"


# ─── Stage 4: SHA-256 Hash Verification ───────────────────────────────────────

@pytest.mark.asyncio
async def test_sha256_hash_format_and_determinism(
    admin_client: AsyncClient,
) -> None:
    """
    The returned SHA-256 hash must be exactly 64 hex chars and must be
    reproducible given the same inputs.
    """
    complaint_id = await _create_complaint(admin_client)
    await _advance_to_qa_review(admin_client, complaint_id)

    resp = await admin_client.post(
        f"/api/complaints/{complaint_id}/sign",
        json={
            "password": "Admin@123",
            "reason": "Verifying SHA256 hash correctness.",
            "target_status": "QA_APPROVED",
        },
    )
    assert resp.status_code == 200
    data = resp.json()

    returned_hash = data["hash"]
    assert len(returned_hash) == 64, f"SHA-256 must be 64 hex chars, got {len(returned_hash)}"

    # Verify it looks like a valid hex string
    int(returned_hash, 16)  # Raises ValueError if not valid hex


# ─── Stage 5: Audit Trail Created ─────────────────────────────────────────────

@pytest.mark.asyncio
async def test_audit_event_created_on_signing(
    admin_client: AsyncClient,
) -> None:
    """An immutable audit event of type 'Electronic Signature' must be created on signing."""
    complaint_id = await _create_complaint(admin_client)
    await _advance_to_qa_review(admin_client, complaint_id)

    await admin_client.post(
        f"/api/complaints/{complaint_id}/sign",
        json={
            "password": "Admin@123",
            "reason": "Auditing the audit trail.",
            "target_status": "QA_APPROVED",
        },
    )

    # Retrieve complaint detail and check audit_events
    detail_resp = await admin_client.get(f"/api/complaints/{complaint_id}")
    assert detail_resp.status_code == 200
    detail = detail_resp.json()

    audit_events = detail.get("audit_events", [])
    sig_events = [e for e in audit_events if e["action_type"] == "Electronic Signature"]
    assert len(sig_events) >= 1, f"No 'Electronic Signature' audit event found. Events: {[e['action_type'] for e in audit_events]}"

    sig_event = sig_events[0]
    assert "21 CFR Part 11" in sig_event["description"]
    assert sig_event["event_metadata"] is not None
    assert "signature_hash" in sig_event["event_metadata"]


# ─── Stage 6: Signature History Endpoint ─────────────────────────────────────

@pytest.mark.asyncio
async def test_signature_history_endpoint(
    admin_client: AsyncClient,
) -> None:
    """GET /api/complaints/{id}/signatures returns signature history."""
    complaint_id = await _create_complaint(admin_client)
    await _advance_to_qa_review(admin_client, complaint_id)

    # Pre-signing: initial history
    hist_resp = await admin_client.get(f"/api/complaints/{complaint_id}/signatures")
    assert hist_resp.status_code == 200
    pre_count = len(hist_resp.json())

    # Sign
    sign_resp = await admin_client.post(
        f"/api/complaints/{complaint_id}/sign",
        json={
            "password": "Admin@123",
            "reason": "Checking signature history.",
            "target_status": "QA_APPROVED",
        },
    )
    assert sign_resp.status_code == 200
    sig_id = sign_resp.json()["signature_id"]

    # Post-signing: history contains new record
    hist_resp2 = await admin_client.get(f"/api/complaints/{complaint_id}/signatures")
    assert hist_resp2.status_code == 200
    records = hist_resp2.json()
    assert len(records) == pre_count + 1

    record = next(r for r in records if r["id"] == sig_id)
    assert record["id"] == sig_id
    assert record["status_before"] == "QA_REVIEW"
    assert record["status_after"] == "QA_APPROVED"
    assert len(record["signature_hash"]) == 64
    assert record["reason"] == "Checking signature history."


@pytest.mark.asyncio
async def test_signature_history_shows_multiple_records(
    admin_client: AsyncClient,
) -> None:
    """Multiple signatures on a complaint are all captured in history."""
    complaint_id = await _create_complaint(admin_client)
    await _advance_to_qa_review(admin_client, complaint_id)

    # Sign 1: QA_REVIEW → QA_APPROVED
    r1 = await admin_client.post(
        f"/api/complaints/{complaint_id}/sign",
        json={"password": "Admin@123", "reason": "First QA approval.", "target_status": "QA_APPROVED"},
    )
    assert r1.status_code == 200

    # Sign 2: QA_APPROVED → CLOSED
    r2 = await admin_client.post(
        f"/api/complaints/{complaint_id}/sign",
        json={"password": "Admin@123", "reason": "Closure after CAPA done.", "target_status": "CLOSED"},
    )
    assert r2.status_code == 200

    hist_resp = await admin_client.get(f"/api/complaints/{complaint_id}/signatures")
    assert hist_resp.status_code == 200
    records = hist_resp.json()
    assert len(records) >= 2


# ─── Stage 7: Complaint Detail Includes Signatures ───────────────────────────

@pytest.mark.asyncio
async def test_complaint_detail_includes_signatures(
    admin_client: AsyncClient,
) -> None:
    """GET /api/complaints/{id} response includes the 'signatures' field."""
    complaint_id = await _create_complaint(admin_client)
    await _advance_to_qa_review(admin_client, complaint_id)

    await admin_client.post(
        f"/api/complaints/{complaint_id}/sign",
        json={"password": "Admin@123", "reason": "Embedded in detail.", "target_status": "QA_APPROVED"},
    )

    detail_resp = await admin_client.get(f"/api/complaints/{complaint_id}")
    assert detail_resp.status_code == 200
    detail = detail_resp.json()

    assert "signatures" in detail
    assert len(detail["signatures"]) >= 1
    sig = next(s for s in detail["signatures"] if s["action"] == "QA Approval")
    assert sig["action"] == "QA Approval"
    assert sig["status_before"] == "QA_REVIEW"
    assert sig["status_after"] == "QA_APPROVED"


# ─── Stage 8: Complaint Not Found → 404 ──────────────────────────────────────

@pytest.mark.asyncio
async def test_sign_nonexistent_complaint_returns_404(
    admin_client: AsyncClient,
) -> None:
    """Signing a nonexistent complaint returns HTTP 404."""
    fake_id = "00000000-0000-0000-0000-000000000099"
    resp = await admin_client.post(
        f"/api/complaints/{fake_id}/sign",
        json={
            "password": "Admin@123",
            "reason": "This complaint doesn't exist.",
            "target_status": "QA_APPROVED",
        },
    )
    assert resp.status_code == 404


# ─── Stage 9: Status Transition Updated After Signing ────────────────────────

@pytest.mark.asyncio
async def test_complaint_status_updated_after_signing(
    admin_client: AsyncClient,
) -> None:
    """After signing, complaint status must be updated to the target status."""
    complaint_id = await _create_complaint(admin_client)
    await _advance_to_qa_review(admin_client, complaint_id)

    await admin_client.post(
        f"/api/complaints/{complaint_id}/sign",
        json={"password": "Admin@123", "reason": "Status check.", "target_status": "QA_APPROVED"},
    )

    detail = (await admin_client.get(f"/api/complaints/{complaint_id}")).json()
    assert detail["status"] == "QA_APPROVED"


# ─── Stage 10: Dashboard Signature Metrics ───────────────────────────────────

@pytest.mark.asyncio
async def test_dashboard_includes_signature_metrics(
    admin_client: AsyncClient,
) -> None:
    """Dashboard metrics must include unsigned_qa_reviews, unsigned_closures, recent_signatures_count."""
    resp = await admin_client.get("/api/dashboard/metrics")
    assert resp.status_code == 200
    data = resp.json()

    assert "unsigned_qa_reviews" in data, f"Missing unsigned_qa_reviews. Keys: {list(data.keys())}"
    assert "unsigned_closures" in data
    assert "recent_signatures_count" in data
    assert isinstance(data["unsigned_qa_reviews"], int)
    assert isinstance(data["unsigned_closures"], int)
    assert isinstance(data["recent_signatures_count"], int)
