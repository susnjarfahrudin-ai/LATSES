"""LAT-CES Scientific Data Provenance Object."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


@dataclass(frozen=True)
class ScientificDataObject:
    """Immutable identity-bearing scientific data record."""

    value: Any
    source: Any
    data_id: str | None = None
    timestamp: str | None = None
    transformation: Any = None
    reference: str | None = None

    def __post_init__(self) -> None:
        if self.source is None:
            raise ValueError("ScientificDataObject requires a source")
        data_id = self.data_id or f"SDO-{uuid4().hex.upper()}"
        timestamp = self.timestamp or datetime.now(timezone.utc).isoformat()
        if not data_id.strip():
            raise ValueError("data_id must be non-empty")
        if not timestamp.strip():
            raise ValueError("timestamp must be non-empty")
        object.__setattr__(self, "data_id", data_id)
        object.__setattr__(self, "timestamp", timestamp)

    def to_record(self) -> dict[str, Any]:
        return {
            "data_id": self.data_id,
            "value": self.value,
            "source": self.source,
            "timestamp": self.timestamp,
            "transformation": self.transformation,
            "reference": self.reference,
        }
