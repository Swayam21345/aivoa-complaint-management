import pytest
from httpx import AsyncClient

from app.ai.state import ComplaintState
from app.ai.workflow import complaint_workflow
from app.services.document_parser import clean_email_text, extract_text


@pytest.mark.asyncio
async def test_health_check(async_client: AsyncClient) -> None:
    response = await async_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True
    assert "AICCMS" in data["service"]


@pytest.mark.asyncio
async def test_document_parser_text_and_email() -> None:
    text_result = await extract_text(
        input_type="text",
        raw_text="Product Quality Defect reported for Amoxicillin 500mg Batch B123.",
    )
    assert "Amoxicillin 500mg Batch B123" in text_result

    raw_email = (
        "From: john.doe@pharma.com\n"
        "To: quality@aiccms.com\n"
        "Subject: Defect report\n\n"
        "Tablet discoloration noticed in batch B999."
    )
    email_result = clean_email_text(raw_email)
    assert "From:" not in email_result
    assert "Tablet discoloration noticed in batch B999." in email_result


@pytest.mark.asyncio
async def test_langgraph_workflow() -> None:
    initial_state: ComplaintState = {
        "raw_text": "Customer reported severe packaging damage and leaking bottles for Paracetamol 500mg, Lot #PCT-2026-99.",
        "input_type": "text",
    }
    result = await complaint_workflow.ainvoke(initial_state)
    output = result.get("final_output")
    assert output is not None
    assert "complaint_summary" in output
    assert "category" in output
    assert "risk_level" in output

    # Phase 3.1 QMS AI Copilot Nodes verification
    assert "summary" in output and "short_summary" in output["summary"]
    assert "completeness" in output and "completeness_score" in output["completeness"]
    assert "root_cause" in output and "probable_root_causes" in output["root_cause"]
    assert "capa" in output and "corrective_actions" in output["capa"]
    assert "duplicates" in output and "duplicate_found" in output["duplicates"]
    assert "risk_explanation" in output and "explanation" in output["risk_explanation"]
