from typing import Optional

from mermaid.flowchart import Node, Link, FlowChart  # type: ignore[import-untyped]

from parsers.lr.lr0 import LR0Parser
from parsers.lr.lr_types import lr_state_to_str


def lr_parser_to_mermaid(p: LR0Parser, title: Optional[str] = None) -> FlowChart:
    if title is None:
        title = ""
    nodes = {i: Node(str(i), lr_state_to_str(state)) for i, state in p.states.items()}
    links = []
    for edge in p.edges:
        links.append(
            Link(
                origin=nodes[edge.from_], end=nodes[edge.to], message=f'"{edge.symbol}"'
            )
        )
    return FlowChart(title=title, nodes=list(nodes.values()), links=links)
