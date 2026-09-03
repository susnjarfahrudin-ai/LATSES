"""Read-only umbrella adapter for external visualization/solver backends.

The adapter translates the existing VisualizationRepresentation into a neutral
backend envelope. It never imports, launches, or depends on Blender, ParaView,
or OpenFOAM, and it never creates or mutates a BuildingModel.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

from .visualization_contract import VisualizationRepresentation


VisualizationBackend = Literal["blender", "paraview", "openfoam"]


@dataclass(frozen=True)
class VisualizationBackendEnvelope:
    """Immutable hand-off from LATSES visualization data to an external backend."""

    backend: VisualizationBackend
    representation_id: str
    source_ref: str
    building_model_id: str
    quantity: Any
    value: Any
    unit: Any
    provenance_ref: str
    visualization_attributes: Any
    status: str


def to_visualization_backend_envelope(
    representation: VisualizationRepresentation,
    backend: VisualizationBackend,
) -> VisualizationBackendEnvelope:
    """Expose one canonical representation to a selected external backend."""
    if backend not in {"blender", "paraview", "openfoam"}:
        raise ValueError(f"unsupported visualization backend: {backend!r}")

    return VisualizationBackendEnvelope(
        backend=backend,
        representation_id=representation.representation_id,
        source_ref=representation.source_ref,
        building_model_id=representation.building_model_id,
        quantity=representation.quantity,
        value=representation.value,
        unit=representation.unit,
        provenance_ref=representation.provenance_ref,
        visualization_attributes=representation.visualization_attributes,
        status=representation.status,
    )


__all__ = ["VisualizationBackend", "VisualizationBackendEnvelope", "to_visualization_backend_envelope"]
