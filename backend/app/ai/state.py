from typing import Any, Dict, List, Optional
from typing_extensions import TypedDict


class ComplaintState(TypedDict, total=False):
    """
    Shared state object passed between LangGraph nodes.

    Fields are progressively populated as the graph executes:
      ingest_node       → cleaned_text
      extract_node      → product_name, batch_number, customer_name, complaint_summary, summary
      classify_node     → category, risk_level, risk_explanation
      completeness_node → completeness
      recommend_node    → root_cause, capa, root_cause_recommendation, capa_recommendation
      duplicate_node   → duplicates
      compose_node      → final_output
    """

    # ── Input ──────────────────────────────────────────────────────────────
    raw_text: str
    input_type: str  # pdf | image | email | text
    existing_complaints: Optional[List[Dict[str, Any]]]

    # ── Ingest ────────────────────────────────────────────────────────────
    cleaned_text: Optional[str]

    # ── Extract & Summary ──────────────────────────────────────────────────
    product_name: Optional[str]
    batch_number: Optional[str]
    customer_name: Optional[str]
    complaint_summary: Optional[str]
    summary: Optional[Dict[str, Any]]  # { short_summary, detailed_summary }

    # ── Classify & Risk ───────────────────────────────────────────────────
    category: Optional[str]
    risk_level: Optional[str]  # High | Medium | Low
    risk_explanation: Optional[Dict[str, Any]]  # { risk_level, explanation }

    # ── Completeness ───────────────────────────────────────────────────────
    completeness: Optional[Dict[str, Any]]  # { completeness_score, missing_fields, recommendations }

    # ── Recommend & CAPA ───────────────────────────────────────────────────
    root_cause_recommendation: Optional[str]
    root_cause: Optional[Dict[str, Any]]  # { probable_root_causes, confidence }
    capa_recommendation: Optional[str]
    capa: Optional[Dict[str, Any]]  # { corrective_actions, preventive_actions }

    # ── Duplicate Detection ───────────────────────────────────────────────
    duplicates: Optional[Dict[str, Any]]  # { duplicate_found, similar_complaints, confidence }

    # ── Output ────────────────────────────────────────────────────────────
    final_output: Optional[Dict[str, Any]]
    error: Optional[str]
