from __future__ import annotations
from .evolution_object import ScientificEvolutionObject
from .version_graph import KnowledgeVersionGraph

class ScientificKnowledgeEvolutionEngine:
    def __init__(self) -> None:
        self.versions: dict[str, str] = {}
        self.version_graph = KnowledgeVersionGraph()

    def register(self, knowledge_id: str, version: str, parent: str | None = None) -> None:
        if not knowledge_id.strip() or not version.strip():
            raise ValueError("Evolution registration requires knowledge and version identity")
        self.version_graph.add_version(version, parent)
        self.versions[knowledge_id] = version

    def evolve(self, previous_knowledge: str, event: str, new_knowledge: str, reason: str, confidence: float, *, evidence: tuple[str, ...]) -> ScientificEvolutionObject:
        if not evidence:
            raise ValueError("Evolution requires evidence")
        return ScientificEvolutionObject(previous_knowledge, event, new_knowledge, reason, confidence)
