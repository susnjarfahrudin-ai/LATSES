from __future__ import annotations

from dataclasses import dataclass
from numbers import Real


class UncertaintyValidationError(ValueError):
    """Raised when measurement uncertainty is invalid."""


@dataclass(frozen=True)
class Uncertainty:
    """Measurement uncertainty record; confidence is expressed as percent when supplied."""

    value: float
    method: str
    confidence: float | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.value, Real) or self.value < 0:
            raise UncertaintyValidationError("uncertainty value must be non-negative")
        if not isinstance(self.method, str) or not self.method.strip():
            raise UncertaintyValidationError("uncertainty method must be non-empty")
        if self.confidence is not None and not 0.0 <= self.confidence <= 100.0:
            raise UncertaintyValidationError("confidence must be between 0 and 100 percent")

    def to_record(self) -> dict[str, object]:
        return {
            "value": float(self.value),
            "method": self.method,
            "confidence": self.confidence,
        }


__all__ = ["Uncertainty", "UncertaintyValidationError"]
