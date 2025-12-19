from langgraph.graph import StateGraph, END
from state import ResearchState
from nodes.researcher import researcher
from nodes.writer import writer
from nodes.reviewer import reviewer


def should_continue(state: ResearchState):
    if state["score"] >= 0.8:
        return "end"
    if state["iteration"] >= 5:
        return "end"
    return "researcher"


def build_graph():
    graph = StateGraph(ResearchState)

    graph.add_node("researcher", researcher)
    graph.add_node("writer", writer)
    graph.add_node("reviewer", reviewer)

    graph.set_entry_point("researcher")

    graph.add_edge("researcher", "writer")
    graph.add_edge("writer", "reviewer")

    graph.add_conditional_edges(
        "reviewer",
        should_continue,
        {
            "researcher": "researcher",
            "end": END
        }
    )

    return graph.compile()
