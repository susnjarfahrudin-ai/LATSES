from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json


class CalibrationValidationError(ValueError):
    """Raised when a calibration record is invalid."""


def _hash_payload(payload: dict[str, object]) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class CalibrationRecord:
    """Canonical calibration record linking an instrument to a reference standard."""

    calibration_id: str
    instrument_id: str
    standard: str
    date: str
    certificate: str
    integrity_hash: str = ""

    def __post_init__(self) -> None:
        for name in ("calibration_id", "instrument_id", "standard", "date", "certificate"):
            if not getattr(self, name).strip():
                raise CalibrationValidationError(f"{name} must be non-empty")
        if not self.integrity_hash:
            object.__setattr__(self, "integrity_hash", self.compute_hash())

    @classmethod
    def now(
        cls,
        *,
        calibration_id: str,
        instrument_id: str,
        standard: str,
        certificate: str,
        date: str | None = None,
    ) -> "CalibrationRecord":
        return cls(
            calibration_id=calibration_id,
            instrument_id=instrument_id,
            standard=standard,
            date=date or datetime.now(timezone.utc).date().isoformat(),
            certificate=certificate,
        )

    def canonical_payload(self) -> dict[str, object]:
        return {
            "calibration_id": self.calibration_id,
            "instrument_id": self.instrument_id,
            "standard": self.standard,
            "date": self.date,
            "certificate": self.certificate,
        }

    def compute_hash(self) -> str:
        return _hash_payload(self.canonical_payload())

    def verify_integrity(self) -> bool:
        return self.integrity_hash == self.compute_hash()

    def to_record(self) -> dict[str, object]:
        payload = self.canonical_payload()
        payload["integrity_hash"] = self.integrity_hash
        return payload


__all__ = ["CalibrationRecord", "CalibrationValidationError"]
