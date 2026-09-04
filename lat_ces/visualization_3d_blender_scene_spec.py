"""Blender-facing scene specification derived from the canonical 3-D handoff.

This module remains renderer-runtime independent: it describes what Blender
may interpret, without importing Blender or mutating the canonical scene.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from .visualization_3d_backend_handoff import Visualization3DBackendEnvelope


Primitive3D = Literal["box"]


@dataclass(frozen=True)
class BlenderSceneSpec:
    """Immutable renderer-specific specification for one canonical object."""

    building_model_id: str
    source_ref: str
    object_id: str
    source_element_id: str
    primitive: Primitive3D
    location: tuple[float, float, float]
    dimensions: tuple[float, float, float]
    rotation_z_deg: float
    role: str
    material_ref: str | None


def to_blender_scene_specs(
    envelope: Visualization3DBackendEnvelope,
) -> tuple[BlenderSceneSpec, ...]:
    """Project a Blender-targeted handoff into immutable object specifications."""
    if envelope.backend != "blender":
        raise ValueError("Blender scene specs require a blender backend envelope")

    return tuple(
        BlenderSceneSpec(
            building_model_id=envelope.building_model_id,
            source_ref=envelope.source_ref,
            object_id=item.visual_object_id,
            source_element_id=item.source_element_id,
            primitive="box",
            location=(
                item.geometry.origin_x_m,
                item.geometry.origin_y_m,
                item.geometry.origin_z_m,
            ),
            dimensions=(
                item.geometry.length_m,
                item.geometry.width_m,
                item.geometry.height_m,
            ),
            rotation_z_deg=item.geometry.rotation_z_deg,
            role=item.role,
            material_ref=item.material_ref,
        )
        for item in envelope.scene.objects
    )


__all__ = ["BlenderSceneSpec", "to_blender_scene_specs"]
