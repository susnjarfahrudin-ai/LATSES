import pytest

from lat_ces.gui_reference_house import ReferenceHouseShowroom
from lat_ces.reference_house import ReferenceHouse


def test_reference_house_is_complete_and_deterministic():
    house = ReferenceHouse.default()
    assert len(house.levels) == 3
    assert {level["id"] for level in house.levels} == {"P", "S1", "S2"}
    assert house.data["roof"]["type"] == "dvovodni"
    assert house.data["heating"]["plant_room"] == "P-BOIL"
    assert house.data["joinery"]["glazing"]["panes"] == 3
    summary = house.summary()

    # Acceptance values correspond to the canonical 12 m × 10 m P+2 reference
    # house model and protect against accidental model drift without imposing
    # the stale >350 m² threshold used by the original showcase test.
    assert summary.floor_area_m2 == pytest.approx(338.0, rel=1e-6)
    assert summary.volume_m3 == pytest.approx(946.4, rel=1e-6)
    assert summary.roof_area_m2 == pytest.approx(185.43675226210846, rel=1e-6)
    assert summary.wall_area_m2 == pytest.approx(310.46399999999994, rel=1e-6)
    assert summary.blocks == pytest.approx(6519.743999999999, rel=1e-6)
    assert summary.slab_concrete_m3 == pytest.approx(72.0, rel=1e-6)
    assert summary.heating_load_w == pytest.approx(16920.0, rel=1e-6)
    assert summary.heating_mass_flow_kg_s == pytest.approx(0.46230348598769655, rel=1e-6)
    assert summary.ventilation_m3_h == pytest.approx(804.44, rel=1e-6)
    assert summary.lighting_w == pytest.approx(630.4, rel=1e-6)


def test_heating_circuits_energy_scenarios_and_comfort_guidance():
    house = ReferenceHouse.default()
    circuits = house.heating_circuits()
    assert len(circuits) == 3
    assert circuits[0].type == "underfloor"
    assert circuits[1].type == "radiator"
    assert circuits[0].delta_t_k == 7.0
    assert circuits[0].mass_flow_kg_s > 0
    assert len(house.envelope_scenarios()) == 4
    assert house.envelope_scenarios()[1]["u_w_m2k"] < house.envelope_scenarios()[0]["u_w_m2k"]
    assert len(house.glazing_scenarios()) == 3
    assert house.simulation_guidance(0.05).startswith("Vrlo blago")
    assert house.simulation_guidance(0.25).startswith("Visoko")


def test_showroom_entrypoint_is_importable():
    assert ReferenceHouseShowroom.__name__ == "ReferenceHouseShowroom"
