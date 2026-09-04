from dataclasses import FrozenInstanceError

import pytest

from lat_ces.visualization_3d_blender_adapter import (
    to_blender_object_instructions,
)
from lat_ces.visualization_3d_blender_scene_spec import BlenderSceneSpec


def _spec(**overrides: object) -> BlenderSceneSpec:
    values = {
        "building_model_id": "building-1",
        "source_ref": "building://building-1",
        "object_id": "wall-1",
        "source_element_id": "wall-1",
        "primitive": "box",
        "location": (1.0, 2.0, 3.0),
        "dimensions": (4.0, 0.3, 2.8),
        "rotation_z_deg": 90.0,
        "role": "solid",
        "material_ref": "brick",
    }
    values.update(overrides)
    return BlenderSceneSpec(**values)  # type: ignore[arg-type]


def test_maps_spec_to_box_instruction_without_changing_identity_or_geometry() -> None:
    spec = _spec()

    result = to_blender_object_instructions((spec,))

    assert len(result) == 1
    instruction = result[0]
    assert instruction.operation == "create_box"
    assert instruction.object_id == "wall-1"
    assert instruction.source_element_id == "wall-1"
    assert instruction.name == "wall-1"
    assert instruction.location == spec.location
    assert instruction.dimensions == spec.dimensions
    assert instruction.rotation_z_deg == 90.0
    assert instruction.role == "solid"
    assert instruction.material_ref == "brick"


def test_preserves_object_order() -> None:
    first = _spec(object_id="room-1", source_element_id="room-1")
    second = _spec(object_id="opening-1", source_element_id="opening-1", role="void")

    result = to_blender_object_instructions((first, second))

    assert [item.object_id for item in result] == ["room-1", "opening-1"]
    assert [item.role for item in result] == ["solid", "void"]


def test_instruction_is_immutable() -> None:
    instruction = to_blender_object_instructions((_spec(),))[0]

    with pytest.raises(FrozenInstanceError):
        instruction.object_id = "changed"  # type: ignore[misc]
