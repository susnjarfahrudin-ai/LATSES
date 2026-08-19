from lat_ces.building_model.example_model import make_small_reference_house
from lat_ces.building_model.integration import analyze_building
from lat_ces.building_model.systems import HeatingZone, VentilationOpening, WaterBranch
from lat_ces.building_model.validation import Status


def test_small_reference_house_drives_all_first_order_engines():
    model = make_small_reference_house()
    report = analyze_building(model)

    assert model.total_volume_m3() == 448.0
    assert report.airflow.air_changes_per_hour == 0.85
    assert report.airflow.velocity_m_s == 0.05
    assert report.airflow.human_zone_ok is True
    assert report.airflow.flow_m3_h == 380.8

    assert report.water.velocity_m_s > 0.0
    assert report.heating.required_w > 0.0
    assert report.heating.emitter_type == "underfloor"

    assert report.validation
    assert all(result.status is Status.PASS for result in report.validation)


def test_explicit_room_mep_inputs_are_consumed_by_one_model():
    model = make_small_reference_house()
    vents = [
        VentilationOpening("r1_supply", "R1", "supply", 0.10, 0.05, 0.70),
        VentilationOpening("r1_extract", "R1", "extract", 0.10, 0.05, 2.50),
    ]
    water = [WaterBranch("r1_cold", "R1", "cold_water", 0.02, 0.0002, 8.0)]
    heating = [HeatingZone("r1_floor", "R1", "underfloor", 35.0, 28.0)]

    report = analyze_building(
        model,
        ventilation_openings=vents,
        water_branches=water,
        heating_zones=heating,
    )

    assert report.ventilation_openings == vents
    assert report.water_branches == water
    assert report.heating_zones == heating
    assert report.room_results["R1"].heating.emitter_type == "underfloor"
    assert report.room_results["R1"].airflow.velocity_m_s == 0.05
    assert report.room_results["R1"].airflow.human_zone_ok is True
