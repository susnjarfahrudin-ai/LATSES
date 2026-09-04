import pytest

from lat_ces.building.floor_plan import FloorPlan, Point2D, Segment2D, Wall
from lat_ces.building.geometry import Box3D, Point3D
from lat_ces.building.mep import HeatingZone, ensure_mep_registry
from lat_ces.building.model import BuildingModel, Level, Material, Room
from lat_ces.mep.thermal_link import apply_thermal_room_loads_to_heating_zones


def _model_with_zone(lambda_w_mk: float | None) -> tuple[BuildingModel, str]:
    model = BuildingModel(name="MEP thermal link test")
    material = Material(
        name="Test masonry",
        thermal_conductivity=lambda_w_mk,
        dimensions_m=(0.25, 0.20, 0.25),
        product_id="TEST-MASONRY",
    )
    model.add_material(material)

    level = Level(name="Prizemlje", elevation=0.0, height=2.80, length_m=6.0, width_m=4.0)
    plan = FloorPlan(name="Prizemlje")
    for index, (x1, y1, x2, y2) in enumerate(
        ((0.0, 0.0, 6.0, 0.0), (6.0, 0.0, 6.0, 4.0), (6.0, 4.0, 0.0, 4.0), (0.0, 4.0, 0.0, 0.0)),
        start=1,
    ):
        plan.add_wall(
            Wall(
                name=f"Vanjski zid {index}",
                segment=Segment2D(Point2D(x1, y1), Point2D(x2, y2)),
                thickness=0.25,
                exterior=True,
                material_id=material.material_id,
            )
        )
    level.set_floor_plan(plan)
    room = Room(
        name="Dnevna soba",
        footprint=Box3D(Point3D(0.0, 0.0, 0.0), length=6.0, width=4.0, height=2.80),
    )
    level.add_room(room)
    model.add_level(level)

    registry = ensure_mep_registry(model)
    registry.add_heating_zone(
        HeatingZone(
            id="HZ-TEST-001",
            room_id=room.room_id,
            emitter_type="underfloor",
            design_supply_temp_c=35.0,
            design_return_temp_c=30.0,
        )
    )
    return model, room.room_id


def test_thermal_room_load_is_bound_to_existing_heating_zone() -> None:
    model, room_id = _model_with_zone(0.35)
    results = apply_thermal_room_loads_to_heating_zones(
        model,
        design_indoor_c=20.0,
        design_outdoor_c=-10.0,
    )

    assert len(results) == 1
    assert results[0].room_id == room_id
    assert results[0].status == "CALCULATED"
    # Q = U * A * ΔT, with R_si=0.13, R_wall=0.25/0.35, R_se=0.04,
    # A=20 m * 2.80 m, and ΔT=30 K.
    assert results[0].room_heat_load_w == pytest.approx(1899.8384491114698, rel=1e-6)
    zone = model.mep.heating_zones["HZ-TEST-001"]
    assert zone.room_id == room_id
    assert zone.room_heat_load_w == pytest.approx(results[0].room_heat_load_w, rel=1e-12)


def test_missing_lambda_does_not_invent_heating_load() -> None:
    model, _ = _model_with_zone(None)
    results = apply_thermal_room_loads_to_heating_zones(
        model,
        design_indoor_c=20.0,
        design_outdoor_c=-10.0,
    )

    assert results[0].status == "INPUT_REQUIRED"
    assert results[0].room_heat_load_w is None
    assert model.mep.heating_zones["HZ-TEST-001"].room_heat_load_w is None
