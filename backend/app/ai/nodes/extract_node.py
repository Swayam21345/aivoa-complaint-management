import json
import logging
from typing import Any

from groq import Groq

from app.ai.prompts.extract_prompt import EXTRACT_SYSTEM_PROMPT, EXTRACT_USER_TEMPLATE
from app.ai.state import ComplaintState
from app.config import get_settings

logger = logging.getLogger(__name__)


def extract_node(state: ComplaintState) -> ComplaintState:
    text = state.get("cleaned_text") or state.get("raw_text") or ""
    if not text:
        state["product_name"] = None
        state["batch_number"] = None
        state["customer_name"] = None
        state["complaint_summary"] = None
        state["summary"] = {
            "short_summary": "No text provided.",
            "detailed_summary": "No complaint content was provided for summary generation.",
        }
        return state

    settings = get_settings()
    if settings.groq_api_key:
        try:
            client = Groq(api_key=settings.groq_api_key)
            prompt_content = EXTRACT_USER_TEMPLATE.format(cleaned_text=text)
            response = client.chat.completions.create(
                model=settings.groq_model,
                messages=[
                    {"role": "system", "content": EXTRACT_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt_content},
                ],
                response_format={"type": "json_object"},
                temperature=0.1,
            )
            raw_content = response.choices[0].message.content or "{}"
            data: dict[str, Any] = json.loads(raw_content)
            short_summ = data.get("complaint_summary") or text[:150].strip()
            det_summ = data.get("detailed_summary") or text.strip()

            state["product_name"] = data.get("product_name")
            state["batch_number"] = data.get("batch_number")
            state["customer_name"] = data.get("customer_name")
            state["complaint_summary"] = short_summ
            state["summary"] = {
                "short_summary": short_summ,
                "detailed_summary": det_summ,
            }
            return state
        except Exception as exc:
            logger.warning(f"Groq extraction failed: {exc}")

    # Fallback heuristic if Groq API key is missing or call fails
    short_summary = text[:200].strip() + ("..." if len(text) > 200 else "")
    detailed_summary = text.strip()

    state["product_name"] = state.get("product_name") or None
    state["batch_number"] = state.get("batch_number") or None
    state["customer_name"] = state.get("customer_name") or None
    state["complaint_summary"] = short_summary
    state["summary"] = {
        "short_summary": short_summary,
        "detailed_summary": detailed_summary,
    }
    return state
