from lat_ces.building.mep import ensure_mep_registry
from lat_ces.building_model.quantities import to_quantity_view
from lat_ces.gui_launcher import refresh_engineering_summary
from lat_ces.reference_house_workflow import build_reference_house_workflow
from lat_ces.structural.building_model_adapter import to_static_input
from lat_ces.thermal.building_model_adapter import to_thermal_input


def test_complete_summary_reads_one_canonical_model():
    workflow = build_reference_house_workflow()
    model = workflow.model
    quantities = to_quantity_view(model)
    static = to_static_input(model)
    thermal = to_thermal_input(model)
    mep = ensure_mep_registry(model)

    assert quantities.rooms
    assert quantities.walls
    assert quantities.openings
    assert quantities.stairs
    assert quantities.terraces
    assert {wall.wall_id for wall in static.walls} == {wall.wall_id for wall in thermal.walls}
    assert len(mep.all_ventilation_openings) >= 0
    assert callable(refresh_engineering_summary)
