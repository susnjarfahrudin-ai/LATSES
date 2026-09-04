"""Independent append-oriented SMC-ROM decision evidence store.

The store preserves lifecycle decisions independently from bounded operational
selector state. It contains neutral provenance only and never owns model
implementations or selector state.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DecisionRecord:
    """Immutable provenance record for one operational lifecycle decision."""

    decision_id: str
    timestamp: str
    session_id: str
    model_id: str
    model_version: str
    previous_state: str | None
    resulting_state: str
    reason: str
    evidence: str
    applicability_passed: bool
    contract_passed: bool
    supersedes_decision_id: str | None
    selector_version: str

    def __post_init__(self) -> None:
        for name in (
            "decision_id",
            "timestamp",
            "session_id",
            "model_id",
            "model_version",
            "resulting_state",
            "reason",
            "evidence",
            "selector_version",
        ):
            if not getattr(self, name):
                raise ValueError(f"{name} must not be empty")


class DecisionRecordStore:
    """Append-only historical evidence independent of bounded selector state."""

    def __init__(self) -> None:
        self._records: list[DecisionRecord] = []
        self._decision_ids: set[str] = set()

    @property
    def records(self) -> tuple[DecisionRecord, ...]:
        """Return all preserved records in append order."""
        return tuple(self._records)

    def append(self, record: DecisionRecord) -> DecisionRecord:
        """Append one decision; existing historical records cannot be replaced."""
        if record.decision_id in self._decision_ids:
            raise ValueError("decision_id already exists")
        self._records.append(record)
        self._decision_ids.add(record.decision_id)
        return record

    def get(self, decision_id: str) -> DecisionRecord:
        """Return a preserved record by decision identifier."""
        for record in self._records:
            if record.decision_id == decision_id:
                return record
        raise KeyError(decision_id)


__all__ = ["DecisionRecord", "DecisionRecordStore"]
