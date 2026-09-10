from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from lat_ces.scientific.evidence_state import EvidenceState


@dataclass(frozen=True)
class MeasurementEvidence:
    """Immutable evidence reference attached to a hardened measurement."""

    measurement_id: str
    source: str
    description: str
    reference: str
    evidence_state: EvidenceState = EvidenceState.UNKNOWN

    def __post_init__(self) -> None:
        for name in ("measurement_id", "source", "description", "reference"):
            if not getattr(self, name).strip():
                raise ValueError(f"measurement evidence {name} must be non-empty")
        if not isinstance(self.evidence_state, EvidenceState):
            object.__setattr__(self, "evidence_state", EvidenceState(self.evidence_state))

    def to_record(self) -> dict[str, Any]:
        return {
            "measurement_id": self.measurement_id,
            "source": self.source,
            "description": self.description,
            "reference": self.reference,
            "evidence_state": self.evidence_state.value,
        }


__all__ = ["MeasurementEvidence"]