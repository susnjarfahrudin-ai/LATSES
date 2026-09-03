"""Source metadata for scientific data provenance."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DataSource:
    source_id: str
    source_type: str
    description: str
    reference: str | None = None

    def __post_init__(self) -> None:
        if not self.source_id.strip():
            raise ValueError("source_id must be non-empty")
        if not self.source_type.strip():
            raise ValueError("source_type must be non-empty")
        if not self.description.strip():
            raise ValueError("description must be non-empty")

    def to_record(self) -> dict[str, str | None]:
        return {
            "source_id": self.source_id,
            "source_type": self.source_type,
            "description": self.description,
            "reference": self.reference,
        }
