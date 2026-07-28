from typing import Any, Dict, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class AICopilotExplainabilityResponse(BaseModel):
    """
    Response model for GET /api/complaints/{id}/copilot
    Aggregates stored AI copilot analysis results and confidence reasoning.
    """

    complaint_id: UUID
    complaint_number: str
    complaint_summary: Optional[Dict[str, Any]] = None
    completeness: Optional[Dict[str, Any]] = None
    root_causes: Optional[Dict[str, Any]] = None
    capa: Optional[Dict[str, Any]] = None
    duplicate_matches: Optional[Dict[str, Any]] = None
    risk_assessment: Optional[Dict[str, Any]] = None
    reasoning: str = Field(description="Aggregated AI model reasoning summary")
    confidence_scores: Dict[str, float] = Field(
        default_factory=dict,
        description="Confidence scores per node module",
    )
