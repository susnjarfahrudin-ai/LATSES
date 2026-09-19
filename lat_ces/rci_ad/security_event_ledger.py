"""Append-only in-memory ledger for canonical RCI-AD security events.

The ledger preserves event history. It does not overwrite existing events,
make defense decisions, mutate security state, or perform enforcement.
"""
from __future__ import annotations

from .security_event import SecurityEvent


class SecurityEventLedger:
    """Append-only event history with read-only snapshots."""

    def __init__(self) -> None:
        self._events: list[SecurityEvent] = []

    def append(self, event: SecurityEvent) -> None:
        if not isinstance(event, SecurityEvent):
            raise ValueError("event must be a SecurityEvent")
        self._events.append(event)

    def events(self) -> tuple[SecurityEvent, ...]:
        return tuple(self._events)

    def __len__(self) -> int:
        return len(self._events)


__all__ = ["SecurityEventLedger"]
