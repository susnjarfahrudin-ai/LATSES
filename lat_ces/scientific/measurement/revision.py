from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone


def revision_label(revision: int) -> str:
    if revision < 1:
        raise ValueError("revision must be >= 1")
    # A, B, ..., Z, AA, AB, ...
    n = revision
    parts: list[str] = []
    while n:
        n, rem = divmod(n - 1, 26)
        parts.append(chr(65 + rem))
    return "".join(reversed(parts))


@dataclass(frozen=True)
class MeasurementRevision:
    """Immutable link between a previous and a new measurement representation."""

    measurement_id: str
    revision: str
    previous_hash: str
    new_hash: str
    reason: str
    created_at: str

    def __post_init__(self) -> None:
        for name in ("measurement_id", "revision", "previous_hash", "new_hash", "reason", "created_at"):
            if not getattr(self, name).strip():
                raise ValueError(f"{name} must be non-empty")


def create_revision(
    previous_measurement,
    new_measurement,
    *,
    previous_hash: str,
    new_hash: str,
    reason: str,
) -> MeasurementRevision:
    if previous_measurement.measurement_id != new_measurement.measurement_id:
        raise ValueError("Measurement revisions must preserve measurement identity")
    if new_measurement.revision != previous_measurement.revision + 1:
        raise ValueError("Measurement revisions must advance by exactly one")
    if previous_hash == new_hash:
        raise ValueError("A revision must produce a new integrity hash")
    return MeasurementRevision(
        measurement_id=previous_measurement.measurement_id,
        revision=revision_label(new_measurement.revision),
        previous_hash=previous_hash,
        new_hash=new_hash,
        reason=reason,
        created_at=datetime.now(timezone.utc).isoformat(),
    )


__all__ = ["MeasurementRevision", "create_revision", "revision_label"]
