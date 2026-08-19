from lat_ces.building_model import (
    BuildingModel, Level, Room, Wall, Opening,
    calculate_airflow, calculate_water_flow, calculate_heat_load,
    Recommendation, Evidence, validate_model, Status,
)


def test_room_and_level_geometry():
    model = BuildingModel("Test House")
    level = Level("L1", "Ground", 10.0, 10.0, 2.8)
    level.add_room(Room("R1", "Living", 10.0, 8.0, 2.8))
    model.add_level(level)
    assert level.rooms["R1"].volume_m3 == 224.0
    assert model.total_volume_m3() == 224.0


def test_door_is_real_opening_from_zero_to_height():
    wall = Wall("W1", 10.0, 0.20, 2.80)
    wall.add_opening(Opening("door", 0.90, 2.10, sill_height_m=0.0, position_m=3.0))
    assert wall.openings[0].z_bottom_m == 0.0
    assert wall.openings[0].z_top_m == 2.10
    assert wall.solid_vertical_segments() == [(2.10, 2.80)]


def test_window_opening_respects_sill_and_wall_height():
    wall = Wall("W1", 10.0, 0.20, 2.80)
    wall.add_opening(Opening("window", 1.20, 1.20, sill_height_m=0.80, position_m=2.0))
    assert wall.openings[0].z_top_m == 2.0
    assert wall.solid_vertical_segments() == [(0.0, 0.80), (2.0, 2.80)]


def test_airflow_at_005_mps():
    result = calculate_airflow(0.01, 0.05, 50.0)
    assert result.flow_m3_h == 1.8
    assert result.human_zone_ok


def test_water_flow():
    result = calculate_water_flow(0.001, 0.02)
    assert result.velocity_m_s > 0


def test_heating_supports_underfloor_and_radiator():
    underfloor = calculate_heat_load(50, 125, 25, 0.25, 0.5, emitter_type="underfloor")
    radiator = calculate_heat_load(50, 125, 25, 0.25, 0.5, emitter_type="radiator")
    assert underfloor.required_w > 0
    assert radiator.required_w == underfloor.required_w


def test_ai_recommendation_requires_human_decision():
    rec = Recommendation("R-001", "Move inlet", "lower velocity", "better comfort", evidence=[
        Evidence("engineering calculation", "RESEARCH", "HIGH")
    ])
    assert rec.state.value == "PROPOSED"
    rec.accept()
    assert rec.state.value == "ACCEPTED"


def test_validation_reports_pass():
    model = BuildingModel("Test")
    level = Level("L1", "Ground", 10, 10, 2.8)
    wall = Wall("W1", 10, 0.2, 2.8)
    wall.add_opening(Opening("door", 0.9, 2.1, position_m=1))
    level.add_wall(wall)
    model.add_level(level)
    results = validate_model(model)
    assert any(r.status is Status.PASS and r.check == "opening:W1" for r in results)
