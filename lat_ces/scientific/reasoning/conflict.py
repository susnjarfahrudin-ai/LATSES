from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class ReasoningConflict:
    conclusion_a: str
    conclusion_b: str
    trace_a: str
    trace_b: str
    status: str
