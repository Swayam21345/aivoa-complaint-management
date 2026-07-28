"""
Ingest node — normalises raw complaint text before LLM processing.
Phase 1: pass-through stub.
Phase 3: whitespace normalisation, email header stripping, token truncation.
"""
from app.ai.state import ComplaintState


import re
from app.ai.state import ComplaintState


def ingest_node(state: ComplaintState) -> ComplaintState:
    raw = state.get("raw_text", "") or ""
    # Normalize line endings
    cleaned = raw.replace("\r\n", "\n").replace("\r", "\n")
    # Strip excess blank lines
    lines = [line.strip() for line in cleaned.split("\n")]
    non_empty = [line for line in lines if line]
    normalized = "\n".join(non_empty)
    state["cleaned_text"] = normalized if normalized else raw.strip()
    return state
