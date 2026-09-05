from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class EvolutionConflict:
    version_a: str
    version_b: str
    reason: str
    status: str = "UNRESOLVED"
