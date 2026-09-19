"""Immutable canonical RCI-AD security event.

A SecurityEvent records security history without making decisions or
performing enforcement. It is intentionally separate from mutable defense
state and from the DefenseDecision contract.
"""
from __future__ import annotations

from dataclasses import dataclass
import math


@dataclass(frozen=True)
class SecurityEvent:
    """Immutable historical security event record."""

    event_type: str
    source_id: str
    reason: str
    timestamp: float
    sequence: int

    def __post_init__(self) -> None:
        for field_name in ("event_type", "source_id", "reason"):
            value = getattr(self, field_name)
            if not isinstance(value, str) or not value:
                raise ValueError(f"{field_name} must be a non-empty string")
        if not math.isfinite(float(self.timestamp)):
            raise ValueError("timestamp must be finite")
        if not isinstance(self.sequence, int) or isinstance(self.sequence, bool) or self.sequence < 0:
            raise ValueError("sequence must be a non-negative integer")


__all__ = ["SecurityEvent"]
