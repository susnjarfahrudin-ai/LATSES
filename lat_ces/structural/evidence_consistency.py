"""Neutral consistency boundary between preserved decisions and reconstruction.

The consistency check reads preserved decision records, validates the requested
IDs and version agreement, and returns immutable evidence. It never mutates the
store, activates a candidate, executes a model, or owns selector state.
"""
from __future__ import annotations

from dataclasses import dataclass

from lat_ces.structural.decision_record_store import DecisionRecordStore


@dataclass(frozen=True)
class EvidenceConsistencyResult:
    """Immutable result of checking preserved decision evidence."""

    decision_ids: tuple[str, ...]
    model_versions: tuple[str, ...]
    selector_version: str
    consistent: bool
    reason: str


class EvidenceConsistencyChecker:
    """Read-only boundary for validating reconstruction evidence against history."""

    def check(
        self,
        store: DecisionRecordStore,
        decision_ids: tuple[str, ...],
        *,
        model_version: str,
        selector_version: str,
    ) -> EvidenceConsistencyResult:
        if len(set(decision_ids)) != len(decision_ids):
            return EvidenceConsistencyResult(
                decision_ids=decision_ids,
                model_versions=(),
                selector_version=selector_version,
                consistent=False,
                reason="decision_ids must be unique",
            )

        records = []
        for decision_id in decision_ids:
            try:
                records.append(store.get(decision_id))
            except KeyError:
                return EvidenceConsistencyResult(
                    decision_ids=decision_ids,
                    model_versions=(),
                    selector_version=selector_version,
                    consistent=False,
                    reason=f"decision_id not found: {decision_id}",
                )

        model_versions = tuple(record.model_version for record in records)
        selectors_match = all(record.selector_version == selector_version for record in records)
        models_match = all(record.model_version == model_version for record in records)

        if not selectors_match:
            return EvidenceConsistencyResult(
                decision_ids=decision_ids,
                model_versions=model_versions,
                selector_version=selector_version,
                consistent=False,
                reason="selector_version mismatch",
            )
        if not models_match:
            return EvidenceConsistencyResult(
                decision_ids=decision_ids,
                model_versions=model_versions,
                selector_version=selector_version,
                consistent=False,
                reason="model_version mismatch",
            )

        return EvidenceConsistencyResult(
            decision_ids=decision_ids,
            model_versions=model_versions,
            selector_version=selector_version,
            consistent=True,
            reason="consistent",
        )


__all__ = ["EvidenceConsistencyResult", "EvidenceConsistencyChecker"]
