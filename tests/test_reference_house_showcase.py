import pytest

from lat_ces.gui_reference_house import ReferenceHouseShowroom
from lat_ces.reference_house import ReferenceHouse


def test_reference_house_is_complete_and_deterministic():
    house = ReferenceHouse.default()
    assert len(house.levels) == 4
    assert {level["id"] for level in house.levels} == {"P", "S1", "S2", "S3"}
    assert house.data["roof"]["type"] == "dvovodni"
    assert house.data["heating"]["plant_room"] == "P-BOIL"
    assert house.data["joinery"]["glazing"]["panes"] == 3
    summary = house.summary()

    # Acceptance values correspond to the canonical 12 m × 10 m P+3
    # reference-house model bundled in reference_house_model.json.
    assert summary.floor_area_m2 == pytest.approx(454.0, rel=1e-6)
    assert summary.volume_m3 == pytest.approx(1271.2, rel=1e-6)
    assert summary.roof_area_m2 == pytest.approx(185.43675226210846, rel=1e-6)
    assert summary.wall_area_m2 == pytest.approx(413.952, rel=1e-6)
    assert summary.blocks == pytest.approx(8692.992, rel=1e-6)
    assert summary.slab_concrete_m3 == pytest.approx(96.0, rel=1e-6)
    assert summary.heating_load_w == pytest.approx(23030.0, rel=1e-6)
    assert summary.heating_mass_flow_kg_s == pytest.approx(0.6084757347915243, rel=1e-6)
    assert summary.ventilation_m3_h == pytest.approx(1080.52, rel=1e-6)
    assert summary.lighting_w == pytest.approx(792.0, rel=1e-6)
    assert summary.floor_area_m2 > 330
    assert summary.volume_m3 > 900
    assert summary.roof_area_m2 > 120
    assert summary.wall_area_m2 > 250
    assert summary.blocks > 6000
    assert summary.slab_concrete_m3 > 60
    assert summary.heating_load_w > 15000
    assert summary.heating_mass_flow_kg_s > 0
    assert summary.ventilation_m3_h > 800
    assert summary.lighting_w > 100


def test_heating_circuits_energy_scenarios_and_comfort_guidance():
    house = ReferenceHouse.default()
    circuits = house.heating_circuits()
    assert len(circuits) == 4
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
