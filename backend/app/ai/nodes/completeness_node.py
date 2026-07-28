import logging
from app.ai.state import ComplaintState

logger = logging.getLogger(__name__)


def completeness_node(state: ComplaintState) -> ComplaintState:
    """
    Evaluates complaint data completeness against pharma QMS standards.
    Checks for: product_name, batch_number, customer_name, category, and detail text.
    """
    missing_fields: list[str] = []
    recommendations: list[str] = []

    product_name = state.get("product_name")
    batch_number = state.get("batch_number")
    customer_name = state.get("customer_name")
    category = state.get("category")
    raw_text = state.get("cleaned_text") or state.get("raw_text") or ""

    score = 0

    if product_name and product_name.strip() and product_name.lower() != "unknown":
        score += 25
    else:
        missing_fields.append("product_name")
        recommendations.append("Specify exact product trade name or active pharmaceutical ingredient.")

    if batch_number and batch_number.strip() and batch_number.lower() != "n/a":
        score += 25
    else:
        missing_fields.append("batch_number")
        recommendations.append("Obtain manufacturing batch/lot number to enable batch record review.")

    if customer_name and customer_name.strip() and customer_name.lower() != "unknown":
        score += 20
    else:
        missing_fields.append("customer_name")
        recommendations.append("Capture customer or health care provider contact information.")

    if category and category.strip() and category != "Other":
        score += 15
    else:
        missing_fields.append("category")
        recommendations.append("Select a specific defect classification category.")

    if len(raw_text.strip()) > 30:
        score += 15
    else:
        missing_fields.append("complaint_text")
        recommendations.append("Provide detailed description of the reported defect or event.")

    if not recommendations:
        recommendations.append("Complaint contains all necessary intake metadata for quality triage.")

    state["completeness"] = {
        "completeness_score": min(score, 100),
        "missing_fields": missing_fields,
        "recommendations": recommendations,
    }
    return state
