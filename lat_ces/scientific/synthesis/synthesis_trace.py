from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class SynthesisTrace:
    synthesis_id: str
    inputs: tuple[str, ...]
    method: str
    output: str
    validation_status: str = "UNKNOWN"
    confidence: float = 0.0
