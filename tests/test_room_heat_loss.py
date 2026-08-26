import pytest

from lat_ces.building.floor_plan import FloorPlan, Point2D, Segment2D, Wall
from lat_ces.building.geometry import Box3D, Point3D
from lat_ces.building.model import BuildingModel, Level, Material, Room
from lat_ces.catalog.product_binding import ensure_product_binding_registry
from lat_ces.reference_house_workflow import build_reference_house_workflow
from lat_ces.thermal.room_heat_loss import calculate_room_heat_losses


def _build_two_room_model(lambda_w_mk: float | None = 0.35) -> BuildingModel:
    model = BuildingModel(name="Thermal test")
    material = Material(
        name="Test masonry",
        thermal_conductivity=lambda_w_mk,
        dimensions_m=(0.25, 0.20, 0.25),
        product_id="TEST-MASONRY",
    )
    model.add_material(material)

    level = Level(name="Prizemlje", elevation=0.0, height=2.80, length_m=6.0, width_m=4.0)
    plan = FloorPlan(name="Prizemlje")
    exterior_segments = (
        (0.0, 0.0, 6.0, 0.0),
        (6.0, 0.0, 6.0, 4.0),
        (6.0, 4.0, 0.0, 4.0),
        (0.0, 4.0, 0.0, 0.0),
    )
    for index, (x1, y1, x2, y2) in enumerate(exterior_segments, start=1):
        plan.add_wall(
            Wall(
                name=f"Vanjski zid {index}",
                segment=Segment2D(Point2D(x1, y1), Point2D(x2, y2)),
                thickness=0.25,
                exterior=True,
                material_id=material.material_id,
            )
        )
    plan.add_wall(
        Wall(
            name="Pregrada",
            segment=Segment2D(Point2D(3.0, 0.0), Point2D(3.0, 4.0)),
            thickness=0.12,
            exterior=False,
            material_id=material.material_id,
        )
    )
    level.set_floor_plan(plan)

    rooms = (
        Room(
            name="Dnevna soba",
            footprint=Box3D(Point3D(0.0, 0.0, 0.0), length=3.0, width=4.0, height=2.80),
        ),
        Room(
            name="Kuhinja",
            footprint=Box3D(Point3D(3.0, 0.0, 0.0), length=3.0, width=4.0, height=2.80),
        ),
    )
    for room in rooms:
        level.add_room(room)
    model.add_level(level)

    registry = ensure_product_binding_registry(model)
    for wall in plan.walls.values():
        if wall.exterior:
            registry.bind(wall.wall_id, "wall", "TEST-MASONRY")
    return model


def test_room_heat_loss_calculates_from_canonical_wall_geometry() -> None:
    model = _build_two_room_model()
    results = calculate_room_heat_losses(model, design_indoor_c=20.0, design_outdoor_c=-10.0)

    assert [result.room_name for result in results] == ["Dnevna soba", "Kuhinja"]
    assert all(result.status == "CALCULATED" for result in results)
    assert all(result.exterior_wall_area_m2 == pytest.approx(28.0) for result in results)
    assert all(result.u_value_w_m2k == pytest.approx(1.130841, rel=1e-5) for result in results)
    assert all(result.design_delta_t_k == pytest.approx(30.0) for result in results)
    assert all(result.heat_loss_w == pytest.approx(949.579, rel=1e-4) for result in results)
    assert all(result.heat_loss_w_m2 == pytest.approx(79.132, rel=1e-4) for result in results)


def test_missing_lambda_is_explicit_input_required() -> None:
    model = _build_two_room_model(lambda_w_mk=None)
    results = calculate_room_heat_losses(model, design_indoor_c=20.0, design_outdoor_c=-10.0)

    assert results
    assert all(result.status == "INPUT_REQUIRED" for result in results)
    assert all(result.heat_loss_w is None for result in results)
    assert all(any("nedostaje λ" in finding for finding in result.findings) for result in results)


def test_reference_house_remains_input_required_without_invented_lambda() -> None:
    workflow = build_reference_house_workflow()
    results = calculate_room_heat_losses(workflow.model, design_indoor_c=20.0, design_outdoor_c=-10.0)

    conditioned = [result for result in results if result.floor_area_m2 > 0.0]
    assert conditioned
    assert all(result.status == "INPUT_REQUIRED" for result in conditioned)


def test_invalid_design_delta_t_is_rejected() -> None:
    model = _build_two_room_model()
    with pytest.raises(ValueError, match="Design indoor temperature"):
        calculate_room_heat_losses(model, design_indoor_c=-5.0, design_outdoor_c=0.0)
