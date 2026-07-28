import json
import logging
from typing import Any

from groq import Groq

from app.ai.prompts.recommend_prompt import RECOMMEND_SYSTEM_PROMPT, RECOMMEND_USER_TEMPLATE
from app.ai.state import ComplaintState
from app.config import get_settings

logger = logging.getLogger(__name__)


def recommend_node(state: ComplaintState) -> ComplaintState:
    product_name = state.get("product_name") or "Unknown Product"
    batch_number = state.get("batch_number") or "N/A"
    category = state.get("category") or "Other"
    risk_level = state.get("risk_level") or "Low"
    summary = state.get("complaint_summary") or state.get("cleaned_text") or "Complaint received."

    settings = get_settings()
    if settings.groq_api_key:
        try:
            client = Groq(api_key=settings.groq_api_key)
            prompt_content = RECOMMEND_USER_TEMPLATE.format(
                product_name=product_name,
                batch_number=batch_number,
                category=category,
                risk_level=risk_level,
                complaint_summary=summary,
            )
            response = client.chat.completions.create(
                model=settings.groq_model,
                messages=[
                    {"role": "system", "content": RECOMMEND_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt_content},
                ],
                response_format={"type": "json_object"},
                temperature=0.2,
            )
            raw_content = response.choices[0].message.content or "{}"
            data: dict[str, Any] = json.loads(raw_content)

            root_causes = data.get("probable_root_causes") or [
                data.get("root_cause_recommendation") or f"Process variance in {category} processing."
            ]
            confidence = float(data.get("confidence") or 0.85)

            corrective = data.get("corrective_actions") or [
                f"Quarantine batch {batch_number} and initiate quality investigation."
            ]
            preventive = data.get("preventive_actions") or [
                "Review batch record execution and recalibrate manufacturing sensors."
            ]

            state["root_cause"] = {
                "probable_root_causes": root_causes,
                "confidence": confidence,
            }
            state["capa"] = {
                "corrective_actions": corrective,
                "preventive_actions": preventive,
            }
            state["root_cause_recommendation"] = "\n• ".join(["Probable Root Causes:"] + root_causes)
            state["capa_recommendation"] = (
                "Corrective Actions:\n• " + "\n• ".join(corrective) + "\n\nPreventive Actions:\n• " + "\n• ".join(preventive)
            )
            return state
        except Exception as exc:
            logger.warning(f"Groq recommendation failed: {exc}")

    # Fallback if Groq API key is missing or call fails
    root_causes = [
        f"Operational or environmental variance during batch {batch_number} production.",
        f"Material packaging integrity anomaly related to {category}.",
    ]
    corrective = [
        f"Quarantine affected batch {batch_number} across warehouse locations.",
        "Perform visual and analytical quality control testing on retained samples.",
    ]
    preventive = [
        "Audit supplier Certificate of Analysis (CoA) parameters.",
        "Update inline inspection SOP and recalibrate packaging line sensors.",
    ]

    state["root_cause"] = {
        "probable_root_causes": root_causes,
        "confidence": 0.85,
    }
    state["capa"] = {
        "corrective_actions": corrective,
        "preventive_actions": preventive,
    }
    state["root_cause_recommendation"] = "\n• ".join(["Probable Root Causes:"] + root_causes)
    state["capa_recommendation"] = (
        "Corrective Actions:\n• " + "\n• ".join(corrective) + "\n\nPreventive Actions:\n• " + "\n• ".join(preventive)
    )
    return state
