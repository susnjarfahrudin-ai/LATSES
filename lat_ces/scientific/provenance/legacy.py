"""Legacy provenance ledger compatibility for LAT-CES Scientific Core."""
from __future__ import annotations

from dataclasses import dataclass, asdict
import json
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ProvenanceRecord:
    event: str
    metrics: dict[str, Any]
    source: str | None = None
    model_id: str | None = None
    revision: str | None = None


class ScientificProvenance:
    """Compatibility facade for the legacy append-only provenance ledger.

    The facade preserves the existing record/history contract while the new
    provenance engine remains the canonical scientific data model.
    """

    def __init__(self, path: str):
        self.path = Path(path)

    def record(
        self,
        event: str,
        metrics: dict[str, Any],
        *,
        source: str | None = None,
        model_id: str | None = None,
        revision: str | None = None,
    ) -> ProvenanceRecord:
        record = ProvenanceRecord(
            event=event,
            metrics=dict(metrics),
            source=source,
            model_id=model_id,
            revision=revision,
        )
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(asdict(record), sort_keys=True) + "\n")
        return record

    def history(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        records: list[dict[str, Any]] = []
        with self.path.open("r", encoding="utf-8") as handle:
            for line in handle:
                if line.strip():
                    records.append(json.loads(line))
        return records
