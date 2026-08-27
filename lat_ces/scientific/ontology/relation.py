from __future__ import annotations
from dataclasses import dataclass

ALLOWED_RELATION_TYPES = (
    "IS_A", "PART_OF", "CAUSES", "DEPENDS_ON",
    "MEASURED_BY", "DERIVED_FROM", "VALIDATED_BY",
)

@dataclass(frozen=True)
class ScientificRelation:
    source_id: str
    relation_type: str
    target_id: str

    def __post_init__(self) -> None:
        if self.relation_type not in ALLOWED_RELATION_TYPES:
            raise ValueError(f"Unknown ontology relation: {self.relation_type}")
        if not self.source_id.strip() or not self.target_id.strip():
            raise ValueError("Ontology relation requires source and target identity")
