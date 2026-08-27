from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class OntologyRevision:
    entity_id: str
    previous_version: str
    new_version: str
    reason: str
    def __post_init__(self) -> None:
        if not self.entity_id.strip() or not self.previous_version.strip() or not self.new_version.strip() or not self.reason.strip():
            raise ValueError("OntologyRevision requires identity, versions and reason")
