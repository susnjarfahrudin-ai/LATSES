from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone

@dataclass(frozen=True)
class EvolutionEvent:
    event_id: str
    trigger: str
    previous_state: str
    new_state: str
    evidence: tuple[str, ...]
    authority: str
    timestamp: str = ""

    def __post_init__(self) -> None:
        if not self.timestamp:
            object.__setattr__(self, "timestamp", datetime.now(timezone.utc).isoformat())
        if not all(value.strip() for value in (self.event_id, self.trigger, self.previous_state, self.new_state, self.authority)):
            raise ValueError("EvolutionEvent requires identity, trigger, states and authority")
        if not self.evidence:
            raise ValueError("EvolutionEvent requires evidence")
