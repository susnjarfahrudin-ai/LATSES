from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class ReasoningTrace:
    reasoning_id: str
    steps: tuple[str, ...]
    def __post_init__(self) -> None:
        if not self.reasoning_id.strip() or not self.steps:
            raise ValueError("ReasoningTrace requires identity and steps")
