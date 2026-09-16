from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from lat_ces.scientific.evidence_state import EvidenceState


@dataclass(frozen=True)
class PropertyInstance:
    """Immutable identity-bearing engineering property evidence.

    This object records a concrete property occurrence. It does not grant
    computational authority, perform admission, or replace the canonical
    verification/governance engine.
    """

    property_id: str
    subject_id: str
    value: Any
    unit: str
    source: str
    provenance: str
    revision: int = 1
    validity: str = ""
    scope: str = ""
    evidence_id: str = ""
    evidence_state: EvidenceState = EvidenceState.UNKNOWN
    verification_record_id: str = ""

    def __post_init__(self) -> None:
        required = (
            ("property_id", self.property_id),
            ("subject_id", self.subject_id),
            ("unit", self.unit),
            ("source", self.source),
            ("provenance", self.provenance),
        )
        for name, value in required:
            if not value.strip():
                raise ValueError(f"property instance {name} must be non-empty")
        if self.revision < 1:
            raise ValueError("property instance revision must be >= 1")
        if not self.evidence_id.strip():
            raise ValueError("property instance evidence_id must be non-empty")
        if not isinstance(self.evidence_state, EvidenceState):
            object.__setattr__(self, "evidence_state", EvidenceState(self.evidence_state))
        if self.evidence_state is EvidenceState.VERIFIED and not self.verification_record_id.strip():
            raise ValueError("VERIFIED property instance requires a verification record")

    def to_record(self) -> dict[str, Any]:
        return {
            "property_id": self.property_id,
            "subject_id": self.subject_id,
            "value": self.value,
            "unit": self.unit,
            "source": self.source,
            "provenance": self.provenance,
            "revision": self.revision,
            "validity": self.validity,
            "scope": self.scope,
            "evidence_id": self.evidence_id,
            "evidence_state": self.evidence_state.value,
            "verification_record_id": self.verification_record_id,
        }


__all__ = ["PropertyInstance"]
