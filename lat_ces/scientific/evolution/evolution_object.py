from __future__ import annotations
from dataclasses import dataclass
from uuid import uuid4

@dataclass(frozen=True)
class ScientificEvolutionObject:
    previous_knowledge: str
    evolution_event: str
    new_knowledge: str
    reason: str
    confidence: float
    evolution_id: str | None = None

    def __post_init__(self) -> None:
        if self.evolution_id is None:
            object.__setattr__(self, "evolution_id", str(uuid4()))
        if not all(value.strip() for value in (self.previous_knowledge, self.evolution_event, self.new_knowledge, self.reason)):
            raise ValueError("Evolution requires previous, event, new knowledge and reason")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("Evolution confidence must be between 0 and 1")
