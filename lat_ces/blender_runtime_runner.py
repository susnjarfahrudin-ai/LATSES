"""Execute Blender scene instructions inside a real Blender runtime."""
from __future__ import annotations

import importlib
from typing import Any, Iterable

from .visualization_3d_blender_adapter import BlenderObjectInstruction


def _load_bpy() -> Any:
    try:
        return importlib.import_module("bpy")
    except ImportError as exc:
        raise RuntimeError("Blender runtime required") from exc


def run_blender_instructions(
    instructions: Iterable[BlenderObjectInstruction], *, bpy_module: Any | None = None
) -> tuple[Any, ...]:
    bpy = bpy_module if bpy_module is not None else _load_bpy()
    created: list[Any] = []
    for instruction in instructions:
        if instruction.operation != "create_box":
            raise ValueError(f"Unsupported Blender operation: {instruction.operation}")
        bpy.ops.mesh.primitive_cube_add(
            location=instruction.location,
            rotation=(0.0, 0.0, instruction.rotation_z_deg * 3.141592653589793 / 180.0),
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
            materials = bpy.data.materials
            material = materials.get(instruction.material_ref) or materials.new(
                name=instruction.material_ref
            )
            if obj.data.materials:
                obj.data.materials[0] = material
            else:
                obj.data.materials.append(material)
            obj["lat_ces_material_ref"] = instruction.material_ref
        created.append(obj)
    return tuple(created)


__all__ = ["run_blender_instructions"]
