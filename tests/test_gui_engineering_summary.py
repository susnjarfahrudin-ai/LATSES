from lat_ces.gui_launcher import _draw_canonical_elements, refresh_engineering_summary
from lat_ces.reference_house_workflow import build_reference_house_workflow
from lat_ces.structural.building_model_adapter import to_static_input
from lat_ces.thermal.building_model_adapter import to_thermal_input


def test_reference_house_has_named_rooms_for_gui_rendering():
    workflow = build_reference_house_workflow()
    level = next(iter(workflow.model.levels.values()))
    names = {room.name for room in level.rooms.values()}
    assert "Stepenište" in names
    assert "Kuhinja" in names
    assert "Dnevni boravak" in names
    assert len(names) >= 4


def test_engineering_views_read_same_reference_house_model():
    workflow = build_reference_house_workflow()
    static = to_static_input(workflow.model)
    thermal = to_thermal_input(workflow.model)
    assert {wall.wall_id for wall in static.walls} == {wall.wall_id for wall in thermal.walls}


def test_gui_launcher_exposes_canonical_render_and_summary_hooks():
    assert callable(_draw_canonical_elements)
    assert callable(refresh_engineering_summary)
