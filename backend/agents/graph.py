"""Purpose: provide a LangGraph orchestration hook for the scan pipeline.
Inputs: an initial state dictionary and a callable pipeline step.
Outputs: the final state dictionary.
"""

from collections.abc import Callable
from typing import Any


def run_graph(initial_state: dict[str, Any], analyze: Callable[[dict[str, Any]], dict[str, Any]]) -> dict[str, Any]:
    try:
        from langgraph.graph import END, StateGraph
    except ImportError:
        return analyze(initial_state)

    graph = StateGraph(dict)
    graph.add_node("analyze", analyze)
    graph.set_entry_point("analyze")
    graph.add_edge("analyze", END)
    app = graph.compile()
    return app.invoke(initial_state)
