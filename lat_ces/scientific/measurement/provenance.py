from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass(frozen=True)
class MeasurementProvenance:
    """Traceability record for a measurement or scientific observation."""

    source: str
    recorded_by: str
    recorded_at: str
    evidence_id: str | None = None
    source_revision: str | None = None

    def __post_init__(self) -> None:
        if not self.source.strip():
            raise ValueError("Measurement provenance requires a source")
        if not self.recorded_by.strip():
            raise ValueError("Measurement provenance requires recorded_by")
        if not self.recorded_at.strip():
            raise ValueError("Measurement provenance requires recorded_at")

    @classmethod
    def now(
        cls,
        *,
        source: str,
        recorded_by: str,
        evidence_id: str | None = None,
        source_revision: str | None = None,
    ) -> "MeasurementProvenance":
        return cls(
            source=source,
            recorded_by=recorded_by,
            recorded_at=datetime.now(timezone.utc).isoformat(),
            evidence_id=evidence_id,
            source_revision=source_revision,
        )
