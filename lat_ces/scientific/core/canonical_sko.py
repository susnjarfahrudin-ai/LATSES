from __future__ import annotations
from dataclasses import dataclass, field, asdict, is_dataclass
from typing import Any
import hashlib
import json
from uuid import uuid4

@dataclass(frozen=True)
class ScientificKnowledgeObject:
    """Canonical SKO container for traceable scientific knowledge.

    It stores the artifact's identity and evidence lineage without asserting that
    nature itself is true. Released revisions are immutable; change creates a new SKO.
    """
    name: str
    object_type: str
    definition: str
    claim: Any = None
    evidence: tuple[Any, ...] = ()
    provenance: tuple[Any, ...] = ()
    validation: Any = None
    ontology: Any = None
    reasoning: Any = None
    synthesis: Any = None
    evolution: tuple[Any, ...] = ()
    governance: tuple[Any, ...] = ()
    preservation: tuple[Any, ...] = ()
    integrity: str = ""
    trust: Any = None
    assurance: Any = None
    lifecycle: str = "DRAFT"
    conflicts: tuple[Any, ...] = ()
    sko_id: str = field(default_factory=lambda: f"SKO-{uuid4().hex.upper()}")
    revision: int = 1
    parents: tuple[str, ...] = ()

    def canonical_payload(self) -> dict[str, Any]:
        def normalize(value: Any) -> Any:
            if is_dataclass(value):
                return {k: normalize(v) for k, v in asdict(value).items()}
            if isinstance(value, dict):
                return {str(k): normalize(value[k]) for k in sorted(value, key=str)}
            if isinstance(value, (tuple, list)):
                return [normalize(v) for v in value]
            return value
        return normalize({
            "sko_id": self.sko_id, "revision": self.revision, "name": self.name,
            "object_type": self.object_type, "definition": self.definition,
            "claim": self.claim, "evidence": self.evidence, "provenance": self.provenance,
            "validation": self.validation, "ontology": self.ontology, "reasoning": self.reasoning,
            "synthesis": self.synthesis, "evolution": self.evolution, "governance": self.governance,
            "preservation": self.preservation, "integrity": self.integrity, "trust": self.trust,
            "assurance": self.assurance, "lifecycle": self.lifecycle, "conflicts": self.conflicts,
            "parents": self.parents,
        })

    def calculate_hash(self) -> str:
        raw = json.dumps(self.canonical_payload(), sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()
