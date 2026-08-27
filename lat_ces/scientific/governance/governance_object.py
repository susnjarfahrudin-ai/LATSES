from __future__ import annotations
from dataclasses import dataclass
from uuid import uuid4

@dataclass(frozen=True)
class ScientificGovernanceObject:
    rule_set: tuple[str, ...]
    authority: str
    scope: str
    decision_process: str
    status: str
    governance_id: str | None = None

    def __post_init__(self) -> None:
        if self.governance_id is None:
            object.__setattr__(self, "governance_id", str(uuid4()))
        if not self.rule_set or not all(item.strip() for item in self.rule_set):
            raise ValueError("Governance requires a rule set")
        if not all(value.strip() for value in (self.authority, self.scope, self.decision_process, self.status)):
            raise ValueError("Governance requires authority, scope, decision process and status")
