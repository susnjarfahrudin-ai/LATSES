"""Versioned algorithm references used in provenance records."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AlgorithmReference:
    algorithm_id: str
    name: str
    version: str
    validation_status: str
    author: str | None = None

    def __post_init__(self) -> None:
        for name, value in (("algorithm_id", self.algorithm_id), ("name", self.name), ("version", self.version), ("validation_status", self.validation_status)):
            if not value.strip():
                raise ValueError(f"{name} must be non-empty")

    def to_record(self) -> dict[str, str | None]:
        return {
            "algorithm_id": self.algorithm_id,
            "name": self.name,
            "version": self.version,
            "validation_status": self.validation_status,
            "author": self.author,
        }
