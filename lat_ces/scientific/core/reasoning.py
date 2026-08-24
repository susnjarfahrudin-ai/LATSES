from __future__ import annotations

from dataclasses import dataclass, field
from uuid import uuid4


@dataclass(frozen=True)
class ReasoningResult:
    """Traceable deterministic reasoning result."""

    result_id: str
    rule_id: str
    inputs: tuple[str, ...]
    output: object
    assumptions: tuple[str, ...] = field(default_factory=tuple)
    provenance: tuple[str, ...] = field(default_factory=tuple)
    confidence: float | None = None
    validated: bool = False


class ReasoningEngine:
    """Canonical container for explicit, provenance-preserving inference."""

    def infer(
        self,
        *,
        rule_id: str,
        inputs: tuple[str, ...],
        output: object,
        assumptions: tuple[str, ...] = (),
        provenance: tuple[str, ...] = (),
        confidence: float | None = None,
        validated: bool = False,
    ) -> ReasoningResult:
        if not rule_id.strip():
            raise ValueError("Reasoning requires a rule identifier")
        if not inputs:
            raise ValueError("Reasoning requires at least one input")
        if not provenance:
            raise ValueError("Reasoning result requires provenance")
        if confidence is not None and not 0.0 <= confidence <= 1.0:
            raise ValueError("Reasoning confidence must be between 0 and 1")
        return ReasoningResult(
            result_id=f"REASON-{uuid4().hex.upper()}",
            rule_id=rule_id,
            inputs=tuple(inputs),
            output=output,
            assumptions=tuple(assumptions),
            provenance=tuple(provenance),
            confidence=confidence,
            validated=validated,
        )
