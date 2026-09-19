"""Canonical RCI-AD defense decision contract.

The contract represents a defense decision without performing enforcement.
Decision authority and enforcement remain separate boundaries.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class DefenseAction(str, Enum):
    ALLOW = "ALLOW"
    OBSERVE = "OBSERVE"
    THROTTLE = "THROTTLE"
    DROP = "DROP"
    ISOLATE = "ISOLATE"
    RECOVER = "RECOVER"


@dataclass(frozen=True)
class DefenseDecision:
    """Immutable decision output for a later enforcement boundary."""

    action: DefenseAction
    reason: str
    source_id: str
    sequence: int

    def __post_init__(self) -> None:
        if not isinstance(self.action, DefenseAction):
            raise ValueError("action must be a DefenseAction")
        for field_name in ("reason", "source_id"):
            value = getattr(self, field_name)
            if not isinstance(value, str) or not value:
                raise ValueError(f"{field_name} must be a non-empty string")
        if (
            not isinstance(self.sequence, int)
            or isinstance(self.sequence, bool)
            or self.sequence < 0
        ):
            raise ValueError("sequence must be a non-negative integer")


__all__ = ["DefenseAction", "DefenseDecision"]
