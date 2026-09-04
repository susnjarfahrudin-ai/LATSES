"""In-memory provenance graph with explicit lineage edges."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ProvenanceLink:
    source_id: str
    target_id: str


class ProvenanceGraph:
    def __init__(self) -> None:
        self.nodes: dict[str, Any] = {}
        self.links: list[ProvenanceLink] = []

    def add_node(self, node: Any) -> Any:
        node_id = getattr(node, "data_id", None) or getattr(node, "source_id", None)
        if not node_id:
            raise ValueError("provenance node requires an identity")
        self.nodes[node_id] = node
        return node

    def add_link(self, source: Any, target: Any) -> ProvenanceLink:
        source_id = source if isinstance(source, str) else getattr(source, "data_id", None) or getattr(source, "source_id", None)
        target_id = target if isinstance(target, str) else getattr(target, "data_id", None) or getattr(target, "source_id", None)
        if not source_id or not target_id:
            raise ValueError("provenance link requires source and target identities")
        if source_id not in self.nodes or target_id not in self.nodes:
            raise ValueError("provenance link endpoints must be registered nodes")
        link = ProvenanceLink(source_id, target_id)
        if link not in self.links:
            self.links.append(link)
        return link

    def successors(self, node_id: str) -> tuple[str, ...]:
        return tuple(link.target_id for link in self.links if link.source_id == node_id)

    def predecessors(self, node_id: str) -> tuple[str, ...]:
        return tuple(link.source_id for link in self.links if link.target_id == node_id)
