from dataclasses import dataclass

import pytest

from lat_ces.blender_runtime_runner import run_blender_instructions
from lat_ces.visualization_3d_blender_adapter import BlenderObjectInstruction


@dataclass
class FakeMaterial:
    name: str


class FakeMaterials:
    def __init__(self) -> None:
        self._items: dict[str, FakeMaterial] = {}

    def get(self, name: str):
        return self._items.get(name)

    def new(self, name: str) -> FakeMaterial:
        material = FakeMaterial(name)
        self._items[name] = material
        return material


class FakeMaterialSlots(list):
    pass


class FakeObject(dict):
    def __init__(self) -> None:
        super().__init__()
        self.name = "Cube"
        self.location = None
        self.dimensions = None
        self.rotation = None
        self.data = type("Data", (), {"materials": FakeMaterialSlots()})()


class FakeBpy:
    def __init__(self) -> None:
        self.object = FakeObject()
        self.context = type("Context", (), {"object": None})()
        self.data = type("Data", (), {"materials": FakeMaterials()})()
        self.ops = type("Ops", (), {"mesh": self})()

    def primitive_cube_add(self, *, location, rotation) -> None:
        self.object = FakeObject()
        self.object.location = location
        self.object.rotation = rotation
        self.context.object = self.object


def _instruction(**overrides: object) -> BlenderObjectInstruction:
    values = {
        "operation": "create_box",
        "object_id": "wall-1",
        "source_element_id": "wall-1",
        "name": "wall-1",
        "location": (1.0, 2.0, 3.0),
        "dimensions": (4.0, 0.3, 2.8),
        "rotation_z_deg": 90.0,
        "role": "solid",
        "material_ref": "brick",
    }
    values.update(overrides)
    return BlenderObjectInstruction(**values)  # type: ignore[arg-type]


def test_runner_creates_box_and_preserves_lat_ces_identity() -> None:
    bpy = FakeBpy()

    created = run_blender_instructions((_instruction(),), bpy_module=bpy)

    assert len(created) == 1
    obj = created[0]
    assert obj.name == "wall-1"
    assert obj.location == (1.0, 2.0, 3.0)
    assert obj.dimensions == (4.0, 0.3, 2.8)
    assert obj.rotation[2] == pytest.approx(1.57079632679)
    assert obj["lat_ces_object_id"] == "wall-1"
    assert obj["lat_ces_source_element_id"] == "wall-1"
    assert obj["lat_ces_role"] == "solid"
    assert obj["lat_ces_material_ref"] == "brick"
    assert obj.data.materials[0].name == "brick"


def test_runner_preserves_instruction_order() -> None:
    bpy = FakeBpy()
    first = _instruction(object_id="room-1", source_element_id="room-1", name="room-1")
    second = _instruction(object_id="opening-1", source_element_id="opening-1", name="opening-1", role="void", material_ref=None)

    created = run_blender_instructions((first, second), bpy_module=bpy)

    assert [obj["lat_ces_object_id"] for obj in created] == ["room-1", "opening-1"]
    assert [obj["lat_ces_role"] for obj in created] == ["solid", "void"]


def test_runner_rejects_unknown_operation() -> None:
    bpy = FakeBpy()
    instruction = _instruction(operation="delete_object")

    with pytest.raises(ValueError, match="Unsupported Blender operation"):
        run_blender_instructions((instruction,), bpy_module=bpy)
