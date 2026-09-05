from __future__ import annotations

from dataclasses import dataclass
from typing import Any
import hashlib
import json

from .revision import revision_label


def _canonical(value: Any) -> Any:
    if hasattr(value, "to_record"):
        return _canonical(value.to_record())
    if hasattr(value, "symbol") and hasattr(value, "dimension"):
        return {"symbol": value.symbol, "dimension": repr(value.dimension)}
    if isinstance(value, dict):
        return {str(k): _canonical(v) for k, v in sorted(value.items(), key=lambda item: str(item[0]))}
    if isinstance(value, (list, tuple)):
        return [_canonical(v) for v in value]
    return value


def measurement_hash(measurement) -> str:
    """Generate the SCI-CORE-0050 integrity hash over stable measurement fields."""
    data = {
        "id": measurement.measurement_id,
        "quantity": _canonical(measurement.quantity),
        "value": measurement.value,
        "unit": _canonical(measurement.unit),
        "uncertainty": _canonical(measurement.uncertainty),
        "instrument": _canonical(measurement.instrument),
        "calibration": _canonical(measurement.calibration),
        "timestamp": measurement.timestamp,
    }
    encoded = json.dumps(_canonical(data), sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def verify_integrity(measurement, stored_hash: str) -> bool:
    return bool(stored_hash) and measurement_hash(measurement) == stored_hash


@dataclass(frozen=True)
class HardenedMeasurement:
    """SCI-CORE-0050 hardened measurement envelope."""

    measurement: Any
    integrity_hash: str
    revision: str
    audit: Any
    evidence: Any

    def validate(self) -> "HardenedMeasurement":
        from .validation import validate_hardened_measurement
        return validate_hardened_measurement(self)


def harden_measurement(measurement, *, audit, evidence) -> HardenedMeasurement:
    if evidence.measurement_id != measurement.measurement_id:
        raise ValueError("Evidence measurement_id must match measurement identity")
    return HardenedMeasurement(
        measurement=measurement,
        integrity_hash=measurement_hash(measurement),
        revision=revision_label(measurement.revision),
        audit=audit,
        evidence=evidence,
    )


__all__ = ["HardenedMeasurement", "harden_measurement", "measurement_hash", "verify_integrity"]
