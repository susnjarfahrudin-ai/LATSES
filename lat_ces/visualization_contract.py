from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping


@dataclass(frozen=True)
class VisualizationRepresentation:
    """Read-only representation of an authoritative engineering value.

    This contract carries references and display metadata only. It does not
    own, calculate, or mutate engineering results.
    """

    representation_id: str
    engineering_result_id: str
    source_ref: str
    building_model_id: str
    quantity: Any
    value: Any
    unit: Any
    provenance_ref: str
    visualization_attributes: Mapping[str, Any]
    status: str = "READY"

    def __post_init__(self) -> None:
        if not self.representation_id.strip():
            raise ValueError("representation_id is required")
        if not self.engineering_result_id.strip():
            raise ValueError("engineering_result_id is required")
        if not self.source_ref.strip():
            raise ValueError("source_ref is required")
        if not self.building_model_id.strip():
            raise ValueError("building_model_id is required")
        if not self.provenance_ref.strip():
            raise ValueError("provenance_ref is required")


__all__ = ["VisualizationRepresentation"]
