"""Canonical Scientific Provenance contract with a legacy-ledger adapter.

The adapter preserves the existing JSONL storage shape while giving Scientific
Models one stable provenance API. It intentionally does not delete or rewrite
legacy history.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Mapping, Optional

from lat_ces.gov.provenance import ProvenanceLedger


@dataclass(frozen=True)
class ProvenanceRecord:
    event: str
    metrics: Mapping[str, Any]
    timestamp: str
    source: Optional[str] = None
    model_id: Optional[str] = None
    revision: Optional[str] = None


class ScientificProvenance:
    """Canonical provenance facade used by Scientific Model implementations."""

    def __init__(self, file_path: str = "data/provenance_ledger.jsonl") -> None:
        self._ledger = ProvenanceLedger(file_path)

    @property
    def ledger(self) -> ProvenanceLedger:
        return self._ledger

    def record(
        self,
        event: str,
        metrics: Mapping[str, Any],
        *,
        source: Optional[str] = None,
        model_id: Optional[str] = None,
        revision: Optional[str] = None,
    ) -> ProvenanceRecord:
        """Record an event without changing the legacy ledger's metrics shape.

        Legacy consumers expect the caller-supplied metrics to remain directly
        under ``history[*]["metrics"]``. Scientific metadata is therefore kept
        in a reserved ``_scientific`` member rather than nesting the metrics
        mapping itself.
        """
        timestamp = datetime.now(timezone.utc).isoformat()
        record = ProvenanceRecord(
            event=event,
            metrics=dict(metrics),
            timestamp=timestamp,
            source=source,
            model_id=model_id,
            revision=revision,
        )

        legacy_metrics = dict(metrics)
        legacy_metrics["_scientific"] = {
            "timestamp": timestamp,
            "source": source,
            "model_id": model_id,
            "revision": revision,
        }
        self._ledger.record(event, legacy_metrics)
        return record

    def history(self) -> list[dict[str, Any]]:
        return self._ledger.get_history()


__all__ = ["ProvenanceRecord", "ScientificProvenance"]
