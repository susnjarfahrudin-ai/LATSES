from __future__ import annotations
from dataclasses import dataclass
from uuid import uuid4

@dataclass(frozen=True)
class GovernanceEvolutionRecord:
    previous_version: str
    new_version: str
    reason: str
    evidence: tuple[str, ...]
    evolution_id: str = ""
    def __post_init__(self) -> None:
        if not self.evolution_id:
            object.__setattr__(self, "evolution_id", f"GEV-{uuid4().hex.upper()}")
        if not self.evidence:
            raise ValueError("Governance evolution requires evidence")

class GovernanceEvolutionEngine:
    def evolve(self, previous_version: str, new_version: str, reason: str, evidence: tuple[str, ...]) -> GovernanceEvolutionRecord:
        return GovernanceEvolutionRecord(previous_version, new_version, reason, tuple(evidence))
