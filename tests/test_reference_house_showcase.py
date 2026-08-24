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
    # Exact deterministic values for the canonical reference-house model.
    assert summary.floor_area_m2 == 338.0
    assert summary.volume_m3 == 946.4
    assert summary.roof_area_m2 > 120
    assert summary.wall_area_m2 > 250
    assert summary.blocks > 6000
    assert summary.slab_concrete_m3 > 60
    assert summary.heating_load_w > 15000
    assert summary.heating_mass_flow_kg_s > 0
    assert summary.ventilation_m3_h == summary.volume_m3 * 0.85
    assert summary.lighting_w > 100


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
