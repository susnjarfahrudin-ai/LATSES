from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class ScientificRule:
    rule_id: str
    name: str
    domain: str
    description: str
    validity: str = "VALID"

    def __post_init__(self) -> None:
        if not all(v.strip() for v in (self.rule_id, self.name, self.domain, self.description, self.validity)):
            raise ValueError("ScientificRule requires identity, domain, description and validity")
