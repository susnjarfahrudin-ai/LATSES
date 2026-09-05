from __future__ import annotations
from dataclasses import dataclass, field
from uuid import uuid4

@dataclass(frozen=True)
class ScientificReasoningObject:
    premises: tuple[str, ...]
    rule_id: str
    conclusion: str
    confidence: float
    reasoning_id: str | None = None
    trace: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if self.reasoning_id is None:
            object.__setattr__(self, "reasoning_id", str(uuid4()))
        if not self.premises or not self.rule_id.strip() or not self.conclusion.strip():
            raise ValueError("Reasoning requires premises, rule and conclusion")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("Reasoning confidence must be between 0 and 1")
        if not self.trace:
            raise ValueError("Reasoning conclusion requires a trace")
