import json
import logging
from typing import Any

from groq import Groq

from app.ai.prompts.classify_prompt import CLASSIFY_SYSTEM_PROMPT, CLASSIFY_USER_TEMPLATE
from app.ai.state import ComplaintState
from app.config import get_settings

logger = logging.getLogger(__name__)

ALLOWED_CATEGORIES = {
    "Product Quality Defect",
    "Packaging Defect",
    "Labeling Error",
    "Delivery Damage",
    "Adverse Event",
    "Foreign Material",
    "Documentation Error",
    "Other",
}

ALLOWED_RISKS = {"High", "Medium", "Low"}

RISK_EXPLANATIONS: dict[str, str] = {
    "High": (
        "High risk classification assigned due to potential impact on patient safety, "
        "sterility breach, adverse health effects, or critical regulatory non-compliance."
    ),
    "Medium": (
        "Medium risk classification assigned due to moderate quality or packaging defect "
        "that requires root cause investigation and corrective containment."
    ),
    "Low": (
        "Low risk classification assigned for minor aesthetic or documentation discrepancies "
        "with negligible safety or efficacy impact."
    ),
}


def classify_node(state: ComplaintState) -> ComplaintState:
    text = state.get("cleaned_text") or state.get("raw_text") or ""
    product_name = state.get("product_name") or "Unknown"
    summary = state.get("complaint_summary") or text[:200]

    settings = get_settings()
    if settings.groq_api_key:
        try:
            client = Groq(api_key=settings.groq_api_key)
            prompt_content = CLASSIFY_USER_TEMPLATE.format(
                product_name=product_name,
                complaint_summary=summary,
                cleaned_text=text,
            )
            response = client.chat.completions.create(
                model=settings.groq_model,
                messages=[
                    {"role": "system", "content": CLASSIFY_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt_content},
                ],
                response_format={"type": "json_object"},
                temperature=0.1,
            )
            raw_content = response.choices[0].message.content or "{}"
            data: dict[str, Any] = json.loads(raw_content)

            category = data.get("category")
            risk_level = data.get("risk_level")
            explanation = data.get("risk_explanation") or data.get("explanation")

            final_category = category if category in ALLOWED_CATEGORIES else "Other"
            final_risk = risk_level if risk_level in ALLOWED_RISKS else "Medium"
            final_explanation = (
                explanation or RISK_EXPLANATIONS.get(final_risk, RISK_EXPLANATIONS["Medium"])
            )

            state["category"] = final_category
            state["risk_level"] = final_risk
            state["risk_explanation"] = {
                "risk_level": final_risk,
                "explanation": final_explanation,
            }
            return state
        except Exception as exc:
            logger.warning(f"Groq classification failed: {exc}")

    # Fallback if Groq API key is missing or call fails
    final_category = state.get("category") or "Other"
    final_risk = state.get("risk_level") or "Medium"
    state["category"] = final_category
    state["risk_level"] = final_risk
    state["risk_explanation"] = {
        "risk_level": final_risk,
        "explanation": RISK_EXPLANATIONS.get(final_risk, RISK_EXPLANATIONS["Medium"]),
    }
    return state
