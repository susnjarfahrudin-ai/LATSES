from types import SimpleNamespace

import pytest

from lat_ces.thermal.room_heat_loss import (
    ThermalDesignConditions,
    calculate_room_heat_losses,
)


def _model(lambda_value):
    material = SimpleNamespace(
        material_id="MAT-1",
        resolved_product_id="PRODUCT-1",
        manufacturer="Example",
        name="Test wall",
        dimensions_m=(0.25,),
        thermal_conductivity=lambda_value,
        density=800.0,
        compressive_strength_mpa=10.0,
    )
    room = SimpleNamespace(
        room_id="ROOM-1",
        name="Dnevni boravak",
        floor_area=20.0,
        volume=56.0,
    )
    wall = SimpleNamespace(
        wall_id="WALL-1",
        material_id="MAT-1",
        segment=SimpleNamespace(length=5.0),
        thickness=0.25,
        exterior=True,
        load_bearing=True,
        room_ids=("ROOM-1",),
        name="Vanjski zid 1",
        openings=[],
    )
    level = SimpleNamespace(
        rooms={"ROOM-1": room},
        floor_plan=SimpleNamespace(walls={"WALL-1": wall}),
        height=2.8,
    )
    return SimpleNamespace(materials={"MAT-1": material}, levels={"L1": level})


def test_known_lambda_calculates_wall_heat_loss() -> None:
    result = calculate_room_heat_losses(
        _model(0.40),
        ThermalDesignConditions(indoor_temperature_c=20.0, outdoor_temperature_c=-10.0),
    )
    room = result.rooms[0]
    assert result.status == "CALCULATED"
    assert room.calculated_wall_loss_w > 0.0
    assert room.heat_loss_w_m2 > 0.0


def test_missing_lambda_requires_input() -> None:
    result = calculate_room_heat_losses(
        _model(None),
        ThermalDesignConditions(indoor_temperature_c=20.0, outdoor_temperature_c=-10.0),
    )
    assert result.status == "INPUT_REQUIRED"
    assert result.rooms[0].status == "INPUT_REQUIRED"
    assert "nedostaje verificirana λ" in result.rooms[0].findings[0]


def test_design_temperature_delta_must_be_positive() -> None:
    with pytest.raises(ValueError):
        ThermalDesignConditions(indoor_temperature_c=5.0, outdoor_temperature_c=10.0)
