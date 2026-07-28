"""
Compose node — assembles all populated state fields into the final output dict.
"""
from app.ai.state import ComplaintState


def compose_node(state: ComplaintState) -> ComplaintState:
    state["final_output"] = {
        "complaint_summary":         state.get("complaint_summary"),
        "product_name":              state.get("product_name"),
        "batch_number":              state.get("batch_number"),
        "customer_name":             state.get("customer_name"),
        "category":                  state.get("category"),
        "risk_level":                state.get("risk_level"),
        "root_cause_recommendation": state.get("root_cause_recommendation"),
        "capa_recommendation":       state.get("capa_recommendation"),
        "summary":                   state.get("summary"),
        "completeness":              state.get("completeness"),
        "root_cause":                state.get("root_cause"),
        "capa":                      state.get("capa"),
        "duplicates":                state.get("duplicates"),
        "risk_explanation":          state.get("risk_explanation"),
        "error":                     state.get("error"),
    }
    return state
