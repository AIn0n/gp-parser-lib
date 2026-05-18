import pydot

from typing import Optional

from parsers.lr.lr0 import LR0Parser
from parsers.lr.slr import SLRParser
from parsers.lr.lr_types import lr_state_to_str


def lr_parser_to_graphviz(
    p: LR0Parser | SLRParser, title: Optional[str] = None
) -> pydot.Dot:
    if title is None:
        title = ""
    graph = pydot.Dot(title, graph_type="graph", bgcolor="white")
    for i, state in p.states.items():
        graph.add_node(pydot.Node(str(i), label=lr_state_to_str(state)))
    for edge in p.edges:
        dot_edge = pydot.Edge(str(edge.from_), str(edge.to), label=edge.symbol)
        graph.add_edge(dot_edge)
    return graph
