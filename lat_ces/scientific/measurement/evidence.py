from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from lat_ces.scientific.evidence_state import EvidenceState


@dataclass(frozen=True)
class MeasurementEvidence:
    """Immutable measurement evidence with explicit verification lineage."""

    measurement_id: str
    source: str
    description: str
    reference: str
    evidence_state: EvidenceState = EvidenceState.UNKNOWN
    revision: int = 1
    verification_record_id: str = ""

    def __post_init__(self) -> None:
        for name in ("measurement_id", "source", "description", "reference"):
            if not getattr(self, name).strip():
                raise ValueError(f"measurement evidence {name} must be non-empty")
        if self.revision < 1:
            raise ValueError("measurement evidence revision must be >= 1")
        if not isinstance(self.evidence_state, EvidenceState):
            object.__setattr__(self, "evidence_state", EvidenceState(self.evidence_state))
        if self.evidence_state is EvidenceState.VERIFIED and not self.verification_record_id.strip():
            raise ValueError("VERIFIED measurement evidence requires a verification record")

    def to_record(self) -> dict[str, Any]:
        return {
            "measurement_id": self.measurement_id,
            "source": self.source,
            "description": self.description,
            "reference": self.reference,
            "evidence_state": self.evidence_state.value,
            "revision": self.revision,
            "verification_record_id": self.verification_record_id,
        }


__all__ = ["MeasurementEvidence"]
