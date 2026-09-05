from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class SynthesisConflict:
    object_a: str
    object_b: str
    reason: str
    status: str = "UNRESOLVED"
