"""Read-only adapter from VisualizationRepresentation to airflow display data."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .visualization_contract import VisualizationRepresentation


@dataclass(frozen=True)
class AirflowVisualizationData:
    representation_id: str
    building_model_id: str
    quantity: Any
    value: Any
    unit: Any
    provenance_ref: Any
    source_ref: Any
    visualization_attributes: Any


def to_airflow_visualization_data(
    representation: VisualizationRepresentation,
) -> AirflowVisualizationData:
    """Expose representation data for the existing airflow view without mutation."""
    return AirflowVisualizationData(
        representation_id=representation.representation_id,
        building_model_id=representation.building_model_id,
        quantity=representation.quantity,
        value=representation.value,
        unit=representation.unit,
        provenance_ref=representation.provenance_ref,
        source_ref=representation.source_ref,
        visualization_attributes=representation.visualization_attributes,
    )
