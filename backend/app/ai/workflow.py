"""
LangGraph workflow definition for the complaint AI copilot pipeline.
"""
from langgraph.graph import StateGraph, END
from langgraph.graph.state import CompiledStateGraph

from app.ai.state import ComplaintState
from app.ai.nodes.ingest_node import ingest_node
from app.ai.nodes.extract_node import extract_node
from app.ai.nodes.classify_node import classify_node
from app.ai.nodes.completeness_node import completeness_node
from app.ai.nodes.recommend_node import recommend_node
from app.ai.nodes.duplicate_node import duplicate_node
from app.ai.nodes.compose_node import compose_node


def build_workflow() -> CompiledStateGraph:
    """Construct and compile the complaint processing graph."""
    graph: StateGraph = StateGraph(ComplaintState)

    graph.add_node("ingest", ingest_node)
    graph.add_node("extract", extract_node)
    graph.add_node("classify", classify_node)
    graph.add_node("check_completeness", completeness_node)
    graph.add_node("recommend", recommend_node)
    graph.add_node("detect_duplicates", duplicate_node)
    graph.add_node("compose", compose_node)

    graph.set_entry_point("ingest")
    graph.add_edge("ingest", "extract")
    graph.add_edge("extract", "classify")
    graph.add_edge("classify", "check_completeness")
    graph.add_edge("check_completeness", "recommend")
    graph.add_edge("recommend", "detect_duplicates")
    graph.add_edge("detect_duplicates", "compose")
    graph.add_edge("compose", END)

    return graph.compile()


# Compile once at module import; reused for every request.
complaint_workflow = build_workflow()
