"""Transformation records for scientific data lineage."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class TransformationRecord:
    input_id: str
    operation: str
    algorithm_id: str
    output_id: str
    parameters: dict[str, Any] | None = None
    timestamp: str | None = None

    def __post_init__(self) -> None:
        for name, value in (("input_id", self.input_id), ("operation", self.operation), ("algorithm_id", self.algorithm_id), ("output_id", self.output_id)):
            if not value.strip():
                raise ValueError(f"{name} must be non-empty")

    def to_record(self) -> dict[str, Any]:
        return {
            "input_id": self.input_id,
            "operation": self.operation,
            "algorithm_id": self.algorithm_id,
            "output_id": self.output_id,
            "parameters": self.parameters or {},
            "timestamp": self.timestamp,
        }
