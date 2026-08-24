from __future__ import annotations

from dataclasses import dataclass
from uuid import uuid4


@dataclass(frozen=True)
class SynthesisResult:
    """Reproducible derived result retaining input lineage and uncertainty."""

    result_id: str
    model_id: str
    inputs: tuple[str, ...]
    output: object
    assumptions: tuple[str, ...]
    provenance: tuple[str, ...]
    uncertainty: float | None
    validated: bool = False


class SynthesisEngine:
    """Canonical synthesis boundary; derived output never becomes an observation."""

    def synthesize(
        self,
        *,
        model_id: str,
        inputs: tuple[str, ...],
        output: object,
        assumptions: tuple[str, ...] = (),
        provenance: tuple[str, ...] = (),
        uncertainty: float | None = None,
        validated: bool = False,
    ) -> SynthesisResult:
        if not model_id.strip():
            raise ValueError("Synthesis requires a model identifier")
        if not inputs:
            raise ValueError("Synthesis requires at least one input")
        if not provenance:
            raise ValueError("Synthesis result requires provenance")
        if uncertainty is not None and uncertainty < 0:
            raise ValueError("Synthesis uncertainty cannot be negative")
        return SynthesisResult(
            result_id=f"SYN-{uuid4().hex.upper()}",
            model_id=model_id,
            inputs=tuple(inputs),
            output=output,
            assumptions=tuple(assumptions),
            provenance=tuple(provenance),
            uncertainty=uncertainty,
            validated=validated,
        )
