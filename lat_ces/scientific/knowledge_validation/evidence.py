from dataclasses import dataclass
from uuid import uuid4


@dataclass(frozen=True)
class ScientificEvidence:
    evidence_type: str
    source: str
    provenance_id: str
    integrity_status: str
    evidence_id: str | None = None
    measurement_id: str | None = None

    def __post_init__(self) -> None:
        if not self.evidence_type.strip():
            raise ValueError("Evidence type is required")
        if not self.source.strip():
            raise ValueError("Evidence source is required")
        if not self.provenance_id.strip():
            raise ValueError("Evidence provenance is required")
        if self.evidence_id is None:
            object.__setattr__(self, "evidence_id", f"EVID-{uuid4().hex[:12].upper()}")

    @property
    def is_verified(self) -> bool:
        return self.integrity_status.upper() == "VERIFIED"
