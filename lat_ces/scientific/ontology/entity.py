from __future__ import annotations
from dataclasses import dataclass, field
from uuid import uuid4

@dataclass(frozen=True)
class ScientificEntity:
    name: str
    entity_type: str
    definition: str
    entity_id: str | None = None
    domain: str = ""
    version: str = "1"
    provenance: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if self.entity_id is None:
            object.__setattr__(self, "entity_id", str(uuid4()))
        if not self.name.strip() or not self.entity_type.strip() or not self.definition.strip():
            raise ValueError("ScientificEntity requires name, type and definition")
        if not self.domain.strip():
            raise ValueError("ScientificEntity requires a scientific domain")
        if not self.provenance:
            raise ValueError("ScientificEntity requires provenance")
