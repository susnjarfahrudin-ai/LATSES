from types import SimpleNamespace

from lat_ces.gui_context import engineering_context, model_context, selected_wall_properties


def test_selected_wall_properties_is_model_owned():
    wall = SimpleNamespace(
        name="Wall-01",
        thickness=0.20,
        height=2.8,
        load_bearing=True,
        tributary_width_m=3.2,
        material_id="m1",
        openings=["door"],
        segment=SimpleNamespace(length=4.0),
    )
    model = SimpleNamespace(materials={"m1": SimpleNamespace(name="Concrete")})

    result = selected_wall_properties(model, wall)

    assert result["selection"] == "Wall"
    assert result["name"] == "Wall-01"
    assert result["length_m"] == 4.0
    assert result["material"] == "Concrete"
    assert result["opening_count"] == 1


def test_model_context_summarizes_existing_building_model():
    level = SimpleNamespace(
        name="Ground",
        rooms={"r1": object()},
        floor_plan=SimpleNamespace(wall_count=4),
    )
    model = SimpleNamespace(
        name="Reference House",
        levels={"ground": level, "first": SimpleNamespace(rooms={}, floor_plan=None)},
        materials={"m1": object()},
    )

    result = model_context(model)

    assert result == {
        "building": "Reference House",
        "level_count": 2,
        "active_level": "Ground",
        "floor_count": 1,
        "wall_count": 4,
        "room_count": 1,
        "material_count": 1,
    }


def test_engineering_context_preserves_result_statuses():
    report = SimpleNamespace(
        status="INPUT_REQUIRED",
        total_ventilation_flow_m3_h=120.0004,
        total_heating_load_w=1250.001,
        total_water_pressure_drop_pa=18.4567,
        calculated_count=2,
        input_required_count=1,
        conflict_count=0,
    )

    result = engineering_context(report)

    assert result["status"] == "INPUT_REQUIRED"
    assert result["ventilation_m3_h"] == 120.0
    assert result["heating_w"] == 1250.001
    assert result["water_pressure_drop_pa"] == 18.457
    assert result["input_required_count"] == 1
