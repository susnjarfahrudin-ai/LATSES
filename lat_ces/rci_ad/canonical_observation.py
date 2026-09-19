"""Immutable canonical RCI-AD observation data carrier.

This type carries evidence between observation producers and later RCI-AD
components. It does not make security decisions and has no side effects.
Integrity and trust remain separate dimensions by design.
"""
from __future__ import annotations

from dataclasses import dataclass
import math

from .integrity_state import IntegrityState
from .trust_state import TrustState


@dataclass(frozen=True)
class CanonicalObservation:
    source_id: str
    source_type: str
    device_id: str | None
    interface_id: str | None
    module_id: str | None
    data_type: str
    timestamp: float
    measurement: float | None
    unit: str | None
    direction: str | None
    protocol: str | None
    rate: float | None
    size: float | None
    confidence: float
    version: str
    integrity_state: IntegrityState
    trust_state: TrustState
    sequence: int

    def __post_init__(self) -> None:
        for field_name in ("source_id", "source_type", "data_type", "version"):
            value = getattr(self, field_name)
            if not isinstance(value, str) or not value:
                raise ValueError(f"{field_name} must be a non-empty string")
        if not math.isfinite(float(self.timestamp)):
            raise ValueError("timestamp must be finite")
        if self.measurement is not None and not math.isfinite(float(self.measurement)):
            raise ValueError("measurement must be finite when provided")
        if self.rate is not None and (not math.isfinite(float(self.rate)) or float(self.rate) < 0.0):
            raise ValueError("rate must be finite and non-negative when provided")
        if self.size is not None and (not math.isfinite(float(self.size)) or float(self.size) < 0.0):
            raise ValueError("size must be finite and non-negative when provided")
        if not math.isfinite(float(self.confidence)) or not 0.0 <= float(self.confidence) <= 1.0:
            raise ValueError("confidence must be finite and between 0 and 1")
        if not isinstance(self.sequence, int) or isinstance(self.sequence, bool) or self.sequence < 0:
            raise ValueError("sequence must be a non-negative integer")
        if not isinstance(self.integrity_state, IntegrityState):
            raise ValueError("integrity_state must be an IntegrityState")
        if not isinstance(self.trust_state, TrustState):
            raise ValueError("trust_state must be a TrustState")


__all__ = ["CanonicalObservation"]
