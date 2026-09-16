from lat_ces.building.floor_plan import Opening
from lat_ces.building.geometry import Box3D, Point3D
from lat_ces.building.model import BuildingModel, Level, Room, Roof
from lat_ces.building.workflow import make_envelope_floor_plan
from lat_ces.visualization_3d_external import (
    EXTERNAL_3D_SCHEMA,
    build_blender_exchange,
)


def _model() -> BuildingModel:
    plan = make_envelope_floor_plan("Prizemlje", 10.0, 8.0, 0.20)
    wall = next(iter(plan.walls.values()))
    wall.add_opening(Opening(kind="door", offset=1.0, width=0.9, height_m=2.1))
    level = Level(
        name="Prizemlje",
        elevation=0.0,
        height=2.8,
        length_m=10.0,
        width_m=8.0,
        floor_plan=plan,
    )
    level.add_room(
        Room(
            name="Dnevni boravak",
            footprint=Box3D(Point3D(0.2, 0.2, 0.0), 4.0, 3.0, 2.8),
        )
    )
    model = BuildingModel(name="External 3D test")
    model.add_level(level)
    model.set_roof(
        Roof(
            roof_type="Četverovodni",
            covering="Crijep",
            length_m=10.0,
            width_m=8.0,
            height_m=2.5,
        )
    )
    return model


def test_external_blender_exchange_comes_from_canonical_building_model() -> None:
    model = _model()
    payload = build_blender_exchange(model)

    assert payload["schema"] == EXTERNAL_3D_SCHEMA
    assert payload["backend"] == "blender"
    assert payload["building_model_id"] == model.model_id
    assert payload["source_ref"] == f"building-model:{model.model_id}"

    types = [item["role"] for item in payload["objects"]]
    element_types = {item["source_element_id"].split("-", 1)[0] for item in payload["objects"]}
    assert "WALL" in element_types
    assert "OPN" in element_types
    assert "ROOM" in element_types
    assert "ROOF" in element_types
    assert "void" in types


def test_external_blender_exchange_is_data_only_and_does_not_mutate_model() -> None:
    model = _model()
    level = next(iter(model.levels.values()))
    before = (
        model.name,
        tuple(model.levels),
        level.floor_plan.wall_count,
        tuple(wall.wall_id for wall in level.floor_plan.walls.values()),
        model.roof.roof_id if model.roof else None,
    )

    payload = build_blender_exchange(model)

    assert payload["objects"]
    assert (
        model.name,
        tuple(model.levels),
        level.floor_plan.wall_count,
        tuple(wall.wall_id for wall in level.floor_plan.walls.values()),
        model.roof.roof_id if model.roof else None,
    ) == before
