import logging
from typing import Any
from app.ai.state import ComplaintState

logger = logging.getLogger(__name__)


def duplicate_node(state: ComplaintState) -> ComplaintState:
    """
    Scans existing complaints for potential duplicate records based on
    product_name, batch_number, category, or similar complaint text.
    """
    product_name = (state.get("product_name") or "").strip().lower()
    batch_number = (state.get("batch_number") or "").strip().lower()
    cleaned_text = (state.get("cleaned_text") or state.get("raw_text") or "").strip().lower()

    existing_complaints = state.get("existing_complaints") or []
    similar_complaints: list[dict[str, Any]] = []

    if existing_complaints:
        for c in existing_complaints:
            sim_score = 0.0
            c_prod = str(c.get("product_name") or "").strip().lower()
            c_batch = str(c.get("batch_number") or "").strip().lower()
            c_text = str(c.get("complaint_text") or c.get("complaint_summary") or "").strip().lower()

            if batch_number and batch_number != "n/a" and c_batch and c_batch == batch_number:
                sim_score += 0.6

            if product_name and c_prod and c_prod == product_name:
                sim_score += 0.25

            if cleaned_text and c_text and (cleaned_text[:50] in c_text or c_text[:50] in cleaned_text):
                sim_score += 0.25

            if sim_score >= 0.5:
                similar_complaints.append({
                    "complaint_id": c.get("complaint_id") or str(c.get("id")),
                    "similarity_score": min(round(sim_score, 2), 0.99),
                    "summary": c.get("complaint_summary") or c.get("complaint_text") or "Similar complaint recorded.",
                })

    duplicate_found = len(similar_complaints) > 0
    confidence = (
        max([item["similarity_score"] for item in similar_complaints])
        if duplicate_found
        else 0.95
    )

    state["duplicates"] = {
        "duplicate_found": duplicate_found,
        "similar_complaints": similar_complaints,
        "confidence": confidence,
    }
    return state
