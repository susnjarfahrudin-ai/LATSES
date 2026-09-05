"""Execute Blender scene instructions inside a real Blender runtime.

The module keeps ``bpy`` out of import time. Production calls execute inside
Blender, while ``bpy_module`` allows deterministic tests outside Blender.
"""
from __future__ import annotations

import importlib
import math
from typing import Any, Iterable

from .visualization_3d_blender_adapter import BlenderObjectInstruction


def _load_bpy() -> Any:
    try:
        return importlib.import_module("bpy")
    except ImportError as exc:
        raise RuntimeError(
            "The Blender runtime runner must execute inside a Blender Python environment"
        ) from exc


def _get_or_create_material(bpy: Any, material_ref: str) -> Any:
    material = bpy.data.materials.get(material_ref)
    if material is None:
        material = bpy.data.materials.new(name=material_ref)
    return material


def run_blender_instructions(
    instructions: Iterable[BlenderObjectInstruction], *, bpy_module: Any | None = None
) -> tuple[Any, ...]:
    """Execute ``create_box`` instructions using Blender's ``bpy`` API."""
    bpy = bpy_module if bpy_module is not None else _load_bpy()
    created: list[Any] = []

    for instruction in instructions:
        if instruction.operation != "create_box":
            raise ValueError(f"Unsupported Blender operation: {instruction.operation}")

        bpy.ops.mesh.primitive_cube_add(
            location=instruction.location,
            rotation=(0.0, 0.0, math.radians(instruction.rotation_z_deg)),
        )
        obj = bpy.context.object
        if obj is None:
            raise RuntimeError("Blender did not return the created cube object")

        obj.name = instruction.name
        obj.dimensions = instruction.dimensions
        obj["lat_ces_object_id"] = instruction.object_id
        obj["lat_ces_source_element_id"] = instruction.source_element_id
        obj["lat_ces_role"] = instruction.role

        if instruction.material_ref:
            material = _get_or_create_material(bpy, instruction.material_ref)
            if obj.data.materials:
                obj.data.materials[0] = material
            else:
                obj.data.materials.append(material)
            obj["lat_ces_material_ref"] = instruction.material_ref

        created.append(obj)

    return tuple(created)


__all__ = ["run_blender_instructions"]
