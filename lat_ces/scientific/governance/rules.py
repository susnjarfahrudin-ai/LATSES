from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class GovernanceRule:
    rule_id: str
    definition: str
    version: str
    owner: str
    status: str

    def __post_init__(self) -> None:
        if not all(value.strip() for value in (self.rule_id, self.definition, self.version, self.owner, self.status)):
            raise ValueError("GovernanceRule requires all fields")
