"""Deterministic external-renderer exchange for the canonical 3-D scene.

The exchange is deliberately file/data based: LAT-CES owns the immutable
BuildingScene3D and renderer-specific adapters produce a neutral JSON payload.
No external process is executed and no canonical model is mutated here.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from lat_ces.building.model import BuildingModel
from lat_ces.visualization_3d_adapter import to_building_scene_3d
from lat_ces.visualization_3d_backend_handoff import (
    to_visualization_3d_backend_envelope,
)
from lat_ces.visualization_3d_blender_adapter import to_blender_object_instructions
from lat_ces.visualization_3d_blender_scene_spec import to_blender_scene_specs

EXTERNAL_3D_SCHEMA = "latces.visualization.3d.external.blender.v1"


def build_blender_exchange(model: BuildingModel) -> dict[str, Any]:
    """Build one deterministic, renderer-facing Blender exchange payload."""
    scene = to_building_scene_3d(model)
    envelope = to_visualization_3d_backend_envelope(scene, "blender")
    specs = to_blender_scene_specs(envelope)
    instructions = to_blender_object_instructions(specs)

    return {
        "schema": EXTERNAL_3D_SCHEMA,
        "backend": envelope.backend,
        "contract_version": envelope.contract_version,
        "building_model_id": envelope.building_model_id,
        "source_ref": envelope.source_ref,
        "status": envelope.status,
        "objects": [
            {
                "operation": instruction.operation,
                "object_id": instruction.object_id,
                "source_element_id": instruction.source_element_id,
                "name": instruction.name,
                "location": list(instruction.location),
                "dimensions": list(instruction.dimensions),
                "rotation_z_deg": instruction.rotation_z_deg,
                "role": instruction.role,
                "material_ref": instruction.material_ref,
            }
            for instruction in instructions
        ],
    }


def write_blender_exchange(model: BuildingModel, path: str | Path) -> Path:
    """Write the immutable 3-D handoff as UTF-8 JSON without running Blender."""
    target = Path(path)
    target.write_text(
        json.dumps(build_blender_exchange(model), ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return target


__all__ = ["EXTERNAL_3D_SCHEMA", "build_blender_exchange", "write_blender_exchange"]
