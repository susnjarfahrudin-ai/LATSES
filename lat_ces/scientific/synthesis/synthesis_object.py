from __future__ import annotations
from dataclasses import dataclass
from uuid import uuid4

@dataclass(frozen=True)
class ScientificSynthesisObject:
    input_knowledge: tuple[str, ...]
    synthesis_method: str
    generated_structure: str
    confidence: float
    synthesis_id: str | None = None
    trace: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.synthesis_id is None:
            object.__setattr__(self, "synthesis_id", str(uuid4()))
        if not self.input_knowledge or not self.synthesis_method.strip() or not self.generated_structure.strip():
            raise ValueError("Synthesis requires inputs, method and generated structure")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("Synthesis confidence must be between 0 and 1")
        if not self.trace:
            raise ValueError("Synthesis requires a trace")
