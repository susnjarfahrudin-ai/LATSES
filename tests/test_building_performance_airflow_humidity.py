import pytest

from lat_ces.building.reference_house_project import build_reference_house_workflow
from lat_ces.scientific.core.building_performance_domains import (
    AirflowPerformanceAdapter,
    HumidityPerformanceAdapter,
)
from lat_ces.scientific.core.performance_state import (
    BuildingPerformanceState,
    Comparison,
    EvidenceState,
    Provenance,
)


def test_reference_house_airflow_and_humidity_follow_measurement_validation_contract():
    workflow = build_reference_house_workflow()
    level = next(iter(workflow.model.levels.values()))
    room = next(iter(level.rooms.values()))
    performance = BuildingPerformanceState(workflow.model)

    simulation_provenance = Provenance(
        source="building-physics", source_id="reference-house-airflow-rh-v1", model_revision="1"
    )
    measurement_provenance = Provenance(
        source="calibrated-instrument",
        source_id="reference-house-test-bench",
        instrument_id="AIR-RH-01",
        calibration_id="CAL-2026-001",
        timestamp="2026-08-20T18:00:00+02:00",
    )

    airflow = AirflowPerformanceAdapter.from_velocity_area(
        performance,
        level_id=level.level_id,
        room_id=room.room_id,
        velocity_mps=0.40,
        area_m2=0.01,
        uncertainty_m3_s=0.0002,
        provenance=simulation_provenance,
    )
    humidity = HumidityPerformanceAdapter.standard().relative_humidity_observation(
        performance,
        level_id=level.level_id,
        room_id=room.room_id,
        relative_humidity=45.0,
        uncertainty_percent=1.0,
        provenance=simulation_provenance,
    )

    assert airflow.state is EvidenceState.SIMULATED
    assert airflow.value == pytest.approx(0.004)
    assert humidity.state is EvidenceState.SIMULATED

    measured_airflow = performance.observation(
        level_id=level.level_id,
        room_id=room.room_id,
        variable="airflow",
        value=0.0041,
        unit="m3/s",
        state=EvidenceState.MEASURED,
        provenance=measurement_provenance,
        uncertainty=0.0002,
    )
    measured_humidity = performance.observation(
        level_id=level.level_id,
        room_id=room.room_id,
        variable="relative_humidity",
        value=45.4,
        unit="%RH",
        state=EvidenceState.MEASURED,
        provenance=measurement_provenance,
        uncertainty=1.0,
    )

    airflow_comparison = Comparison.compare(airflow, measured_airflow)
    humidity_comparison = Comparison.compare(humidity, measured_humidity)

    assert airflow_comparison.residual == pytest.approx(0.0001)
    assert humidity_comparison.residual == pytest.approx(0.4)
    assert airflow_comparison.validate(0.0005) is EvidenceState.VALIDATED
    assert humidity_comparison.validate(1.0) is EvidenceState.VALIDATED

    assert Comparison.compare(airflow, None).validate(0.0005) is EvidenceState.UNKNOWN
    assert Comparison.compare(humidity, None).validate(1.0) is EvidenceState.UNKNOWN


def test_performance_comparison_rejects_cross_room_measurement():
    workflow = build_reference_house_workflow()
    level = next(iter(workflow.model.levels.values()))
    rooms = list(level.rooms.values())
    if len(rooms) < 2:
        pytest.skip("reference house level has only one room")
    performance = BuildingPerformanceState(workflow.model)
    provenance = Provenance(source="test", source_id="cross-room")
    predicted = performance.observation(
        level_id=level.level_id, room_id=rooms[0].room_id, variable="airflow",
        value=0.004, unit="m3/s", state=EvidenceState.SIMULATED,
        provenance=provenance, uncertainty=0.0002,
    )
    measured = performance.observation(
        level_id=level.level_id, room_id=rooms[1].room_id, variable="airflow",
        value=0.004, unit="m3/s", state=EvidenceState.MEASURED,
        provenance=Provenance(source="instrument", source_id="x", instrument_id="A", calibration_id="C"),
        uncertainty=0.0002,
    )
    with pytest.raises(ValueError, match="share location"):
        Comparison.compare(predicted, measured)
