from examples.test_house_115x8_model import build_test_house
from lat_ces.building.mep import ensure_mep_registry


def test_reference_house_115x8_builds_and_exposes_mep() -> None:
    model, concept = build_test_house()
    registry = ensure_mep_registry(model)

    assert concept.name == "Reference House 11.5 x 8 m"
    assert set(model.levels) == {"ground", "floor1"}
    assert concept.roof is not None
    assert concept.roof.length_m == 11.5
    assert concept.roof.width_m == 8.0
    assert concept.roof.shape.value == "hidden_monopitch"
    assert concept.roof.cover.cover.value == "sheet_metal"

    assert len(registry.all_underfloor_systems) == 2
    assert len(registry.all_underfloor_circuits) == 2
    assert len(registry.all_ventilation_openings) == 32
    assert sum(o.kind == "supply" for o in registry.all_ventilation_openings) == 16
    assert sum(o.kind == "extract" for o in registry.all_ventilation_openings) == 16

    total_ventilation_flow_m3_h = sum(
        opening.design_flow_m3_h for opening in registry.all_ventilation_openings
    )
    assert total_ventilation_flow_m3_h > 0
