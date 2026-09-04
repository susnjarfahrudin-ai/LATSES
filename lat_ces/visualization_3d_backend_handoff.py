"""Renderer-neutral handoff contract for canonical 3-D scenes.

This module defines the boundary between ``BuildingScene3D`` and an external
renderer/backend. It carries the canonical model identity and the immutable
scene as one envelope; it does not serialize, render, execute, or mutate data.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from .visualization_3d_adapter import BuildingScene3D


RendererBackend = Literal["blender", "paraview"]


@dataclass(frozen=True)
class Visualization3DBackendEnvelope:
    """Immutable handoff from LATSES 3-D scene data to a renderer backend."""

    backend: RendererBackend
    contract_version: str
    building_model_id: str
    source_ref: str
    scene: BuildingScene3D
    status: str = "READY"


def to_visualization_3d_backend_envelope(
    scene: BuildingScene3D,
    backend: RendererBackend,
    *,
    contract_version: str = "LAT-VIS-3D-HANDOFF-1",
) -> Visualization3DBackendEnvelope:
    """Wrap one canonical 3-D scene for a selected renderer backend.

    The scene object is passed through unchanged. No renderer-specific
    geometry, file format, process execution, or engineering calculation is
    introduced at this boundary.
    """
    if backend not in {"blender", "paraview"}:
        raise ValueError(f"unsupported 3-D renderer backend: {backend!r}")
    if not contract_version.strip():
        raise ValueError("contract_version is required")

    return Visualization3DBackendEnvelope(
        backend=backend,
        contract_version=contract_version,
        building_model_id=scene.building_model_id,
        source_ref=scene.source_ref,
        scene=scene,
        status=scene.status,
    )


__all__ = [
    "RendererBackend",
    "Visualization3DBackendEnvelope",
    "to_visualization_3d_backend_envelope",
]
