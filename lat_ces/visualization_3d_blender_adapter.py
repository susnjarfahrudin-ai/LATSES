"""Blender runtime handoff derived from :class:`BlenderSceneSpec`.

The core package deliberately does not import ``bpy``.  This adapter produces
renderer-facing instructions that a thin Blender runtime integration can
consume, keeping canonical LAT-CES identity and geometry outside Blender.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from .visualization_3d_blender_scene_spec import BlenderSceneSpec


BlenderOperation = Literal["create_box"]


@dataclass(frozen=True)
class BlenderObjectInstruction:
    """One deterministic Blender operation for one canonical scene object."""

    operation: BlenderOperation
    object_id: str
    source_element_id: str
    name: str
    location: tuple[float, float, float]
    dimensions: tuple[float, float, float]
    rotation_z_deg: float
    role: str
    material_ref: str | None


def to_blender_object_instructions(
    specs: tuple[BlenderSceneSpec, ...],
) -> tuple[BlenderObjectInstruction, ...]:
    """Translate immutable scene specs into deterministic Blender operations.

    No Blender runtime is imported or executed here.  The returned instructions
    are the narrow boundary consumed by a future ``bpy``/Geometry Nodes runner.
    """
    return tuple(
        BlenderObjectInstruction(
            operation="create_box",
            object_id=spec.object_id,
            source_element_id=spec.source_element_id,
            name=spec.object_id,
            location=spec.location,
            dimensions=spec.dimensions,
            rotation_z_deg=spec.rotation_z_deg,
            role=spec.role,
            material_ref=spec.material_ref,
        )
        for spec in specs
    )


__all__ = ["BlenderObjectInstruction", "to_blender_object_instructions"]
