import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_and_list_training_courses(admin_client: AsyncClient) -> None:
    # 1. Create course
    payload = {
        "title": "Good Manufacturing Practice (GMP) Standard Operating Procedure",
        "description": "Annual GxP Compliance & Cleanroom Protocols Training",
        "category": "QUALITY",
        "training_type": "SOP",
        "duration_minutes": 45,
        "passing_score": 80.0,
        "validity_days": 365,
    }
    res = await admin_client.post("/api/training", json=payload)
    assert res.status_code == 201, res.text
    data = res.json()
    assert data["course_number"].startswith("TRN-")
    assert data["title"] == payload["title"]
    assert data["status"] == "DRAFT"
    course_id = data["id"]

    # 2. Update status to ACTIVE
    up_res = await admin_client.patch(f"/api/training/{course_id}", json={"status": "ACTIVE"})
    assert up_res.status_code == 200
    assert up_res.json()["status"] == "ACTIVE"

    # 3. List courses
    list_res = await admin_client.get("/api/training")
    assert list_res.status_code == 200
    assert list_res.json()["total"] >= 1


@pytest.mark.asyncio
async def test_quiz_creation_and_attempt(admin_client: AsyncClient) -> None:
    # Create course
    res = await admin_client.post(
        "/api/training",
        json={
            "title": "Sterile Gowning Procedures SOP",
            "category": "SAFETY",
            "training_type": "SOP",
            "duration_minutes": 30,
            "passing_score": 80.0,
        },
    )
    course_id = res.json()["id"]

    # Add Quiz
    quiz_payload = {
        "title": "Gowning Procedures Comprehension Test",
        "passing_score": 80.0,
        "questions": [
            {
                "question": "What is the primary objective of cleanroom gowning?",
                "option_a": "Fashion compliance",
                "option_b": "Prevent microbial and particulate contamination",
                "option_c": "Thermal insulation",
                "option_d": "Chemical shielding",
                "correct_answer": "B",
                "explanation": "Cleanroom gowning prevents human particle shedding into sterile zones.",
                "display_order": 1,
            }
        ],
    }
    quiz_res = await admin_client.post(f"/api/training/{course_id}/quiz", json=quiz_payload)
    assert quiz_res.status_code == 200, quiz_res.text
    quiz_data = quiz_res.json()
    assert len(quiz_data["questions"]) == 1
    q_id = quiz_data["questions"][0]["id"]

    # Attempt quiz -> 100% PASS
    attempt_res = await admin_client.post(
        f"/api/training/{course_id}/complete",
        json={"answers": [{"question_id": q_id, "selected_option": "B"}]},
    )
    assert attempt_res.status_code == 200
    assert attempt_res.json()["score"] == 100.0
    assert attempt_res.json()["passed"] is True


@pytest.mark.asyncio
async def test_training_assignments(admin_client: AsyncClient, viewer_client: AsyncClient) -> None:
    # Get current user ID
    me_res = await admin_client.get("/api/auth/me")
    admin_id = me_res.json()["id"]

    # Create course
    res = await admin_client.post(
        "/api/training",
        json={"title": "CAPA Investigation Methodology Training", "category": "QUALITY", "training_type": "CAPA"},
    )
    course_id = res.json()["id"]

    # Assign to admin
    assign_res = await admin_client.post(
        f"/api/training/{course_id}/assign",
        json={"user_id": admin_id, "due_days": 15},
    )
    assert assign_res.status_code == 200
    assert assign_res.json()["status"] == "NOT_STARTED"

    # Viewer trying to assign -> 403 Forbidden
    v_assign = await viewer_client.post(
        f"/api/training/{course_id}/assign",
        json={"user_id": admin_id, "due_days": 15},
    )
    assert v_assign.status_code == 403


@pytest.mark.asyncio
async def test_competency_record_and_matrix(admin_client: AsyncClient) -> None:
    me_res = await admin_client.get("/api/auth/me")
    admin_id = me_res.json()["id"]

    # Verify competency
    comp_res = await admin_client.post(
        "/api/training/competency",
        json={"user_id": admin_id, "skill": "Root Cause Analysis (Fishbone & 5-Whys)", "level": "EXPERT"},
    )
    assert comp_res.status_code == 200
    assert comp_res.json()["level"] == "EXPERT"

    # Matrix endpoint
    mat_res = await admin_client.get("/api/training/matrix")
    assert mat_res.status_code == 200
    assert len(mat_res.json()) >= 1


@pytest.mark.asyncio
async def test_training_dashboard_and_reports(admin_client: AsyncClient) -> None:
    dash_res = await admin_client.get("/api/training/dashboard")
    assert dash_res.status_code == 200
    d_data = dash_res.json()
    assert "total_courses" in d_data
    assert "completion_rate_percentage" in d_data

    rep_res = await admin_client.get("/api/training/report")
    assert rep_res.status_code == 200
    assert "competency_matrix" in rep_res.json()
