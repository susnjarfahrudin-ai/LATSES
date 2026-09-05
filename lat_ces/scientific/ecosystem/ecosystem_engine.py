from __future__ import annotations
from dataclasses import dataclass, field
from uuid import uuid4

ECOSYSTEM_STATES = ("UNKNOWN", "INITIALIZED", "CONNECTED", "VALIDATED", "ACTIVE", "EVOLVING", "ARCHIVED")

@dataclass(frozen=True)
class EcosystemNode:
    node_id: str
    node_type: str
    identity: str
    version: str

@dataclass(frozen=True)
class EcosystemRelationship:
    source_id: str
    relation: str
    target_id: str
    provenance: tuple[str, ...] = ()

@dataclass(frozen=True)
class ScientificKnowledgeEcosystemObject:
    ecosystem_id: str
    state: str
    knowledge_objects: tuple[str, ...] = ()
    evidence_objects: tuple[str, ...] = ()
    measurement_sources: tuple[str, ...] = ()
    research_agents: tuple[str, ...] = ()
    institutional_nodes: tuple[str, ...] = ()
    relationships: tuple[EcosystemRelationship, ...] = ()
    conflicts: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.state not in ECOSYSTEM_STATES:
            raise ValueError("Invalid ecosystem state")

class ScientificKnowledgeEcosystemEngine:
    def create(self) -> ScientificKnowledgeEcosystemObject:
        return ScientificKnowledgeEcosystemObject(f"ECO-{uuid4().hex.upper()}", "INITIALIZED")

    def connect(self, ecosystem: ScientificKnowledgeEcosystemObject, *, nodes: tuple[EcosystemNode, ...], relationships: tuple[EcosystemRelationship, ...]) -> ScientificKnowledgeEcosystemObject:
        known = {node.node_id for node in nodes}
        if any(r.source_id not in known or r.target_id not in known for r in relationships):
            raise ValueError("Ecosystem relationship requires registered nodes")
        return ScientificKnowledgeEcosystemObject(ecosystem.ecosystem_id, "CONNECTED", ecosystem.knowledge_objects, ecosystem.evidence_objects, ecosystem.measurement_sources, ecosystem.research_agents, ecosystem.institutional_nodes, relationships, ecosystem.conflicts)
