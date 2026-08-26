from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from .revision import revision_label


@dataclass(frozen=True)
class MeasurementAudit:
    """Immutable audit event for creation or revision of a measurement."""

    measurement_id: str
    action: str
    revision: str
    actor: str
    timestamp: str

    def __post_init__(self) -> None:
        for name in ("measurement_id", "action", "revision", "actor", "timestamp"):
            if not getattr(self, name).strip():
                raise ValueError(f"audit {name} must be non-empty")


def create_audit(measurement, action: str, *, actor: str = "SYSTEM") -> MeasurementAudit:
    if not action.strip():
        raise ValueError("audit action must be non-empty")
    return MeasurementAudit(
        measurement_id=measurement.measurement_id,
        action=action,
        revision=revision_label(measurement.revision),
        actor=actor,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


__all__ = ["MeasurementAudit", "create_audit"]
