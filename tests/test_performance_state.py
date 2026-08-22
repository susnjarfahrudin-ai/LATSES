import pytest

from lat_ces.building_model.core import BuildingModel, Level, Room
from lat_ces.scientific.core.performance_state import (
    BuildingPerformanceState,
    Comparison,
    EvidenceState,
    Provenance,
)


def make_state():
    model = BuildingModel(name="Reference House")
    level = Level("LVL-1", "Ground", 10.0, 10.0, 2.8)
    level.add_room(Room("R1", "Living", 5.0, 4.0, 2.8))
    model.add_level(level)
    return model, BuildingPerformanceState(model)


def test_building_model_is_authoritative_geometry_source():
    model, state = make_state()
    observation = state.observation(
        level_id="LVL-1",
        room_id="R1",
        variable="temperature",
        value=22.0,
        unit="degC",
        state=EvidenceState.SIMULATED,
        provenance=Provenance("RoomDynamicsModel", "room-dynamics-v1", model_revision="rev-a"),
    )
    assert state.building_model is model
    assert observation.building_name == model.name
    assert observation.level_id in model.levels
    assert observation.room_id in model.levels[observation.level_id].rooms


def test_observation_states_are_explicit():
    model, state = make_state()
    for evidence_state in (EvidenceState.ASSUMED, EvidenceState.CALCULATED, EvidenceState.SIMULATED):
        observation = state.observation(
            level_id="LVL-1",
            room_id="R1",
            variable="co2",
            value=700.0,
            unit="ppm",
            state=evidence_state,
            provenance=Provenance("test", evidence_state.value),
        )
        assert observation.state is evidence_state


def test_measured_observation_requires_uncertainty_and_calibration_provenance():
    model, state = make_state()
    provenance = Provenance(
        "sensor", "TEMP-01", instrument_id="TEMP-01", calibration_id="CAL-2026-01"
    )
    measured = state.observation(
        level_id="LVL-1",
        room_id="R1",
        variable="temperature",
        value=22.8,
        unit="degC",
        state=EvidenceState.MEASURED,
        provenance=provenance,
        uncertainty=0.15,
    )
    assert measured.state is EvidenceState.MEASURED
    assert measured.uncertainty == pytest.approx(0.15)
    assert measured.provenance.instrument_id == "TEMP-01"
    assert measured.provenance.calibration_id == "CAL-2026-01"


def test_simulated_and_measured_comparison_uses_same_location_and_variable():
    model, state = make_state()
    predicted = state.observation(
        level_id="LVL-1",
        room_id="R1",
        variable="temperature",
        value=22.4,
        unit="degC",
        state=EvidenceState.SIMULATED,
        provenance=Provenance("RoomDynamicsModel", "room-dynamics-v1"),
        uncertainty=0.10,
    )
    measured = state.observation(
        level_id="LVL-1",
        room_id="R1",
        variable="temperature",
        value=22.8,
        unit="degC",
        state=EvidenceState.MEASURED,
        provenance=Provenance(
            "sensor", "TEMP-01", instrument_id="TEMP-01", calibration_id="CAL-2026-01"
        ),
        uncertainty=0.15,
    )
    comparison = Comparison.compare(predicted, measured)
    assert comparison.residual == pytest.approx(0.4)
    assert comparison.combined_uncertainty == pytest.approx((0.10**2 + 0.15**2) ** 0.5)
    assert comparison.status is EvidenceState.MEASURED


def test_simulated_result_cannot_be_validated_without_measurement():
    model, state = make_state()
    predicted = state.observation(
        level_id="LVL-1",
        room_id="R1",
        variable="co2",
        value=780.0,
        unit="ppm",
        state=EvidenceState.SIMULATED,
        provenance=Provenance("IAQModel", "iaq-v1"),
    )
    comparison = Comparison.compare(predicted, None)
    assert comparison.status is EvidenceState.UNKNOWN
    assert comparison.validate(50.0) is EvidenceState.UNKNOWN


def test_validation_requires_measured_evidence_and_acceptance_tolerance():
    model, state = make_state()
    predicted = state.observation(
        level_id="LVL-1",
        room_id="R1",
        variable="co2",
        value=780.0,
        unit="ppm",
        state=EvidenceState.SIMULATED,
        provenance=Provenance("IAQModel", "iaq-v1"),
    )
    measured = state.observation(
        level_id="LVL-1",
        room_id="R1",
        variable="co2",
        value=810.0,
        unit="ppm",
        state=EvidenceState.MEASURED,
        provenance=Provenance(
            "sensor", "CO2-01", instrument_id="CO2-01", calibration_id="CAL-CO2-01"
        ),
        uncertainty=25.0,
    )
    comparison = Comparison.compare(predicted, measured)
    assert comparison.validate(40.0) is EvidenceState.VALIDATED
    assert comparison.validate(20.0) is EvidenceState.MEASURED


def test_mismatched_location_or_variable_is_rejected():
    model, state = make_state()
    predicted = state.observation(
        level_id="LVL-1", room_id="R1", variable="temperature", value=22.0,
        unit="degC", state=EvidenceState.SIMULATED,
        provenance=Provenance("model", "m1"),
    )
    measured = state.observation(
        level_id="LVL-1", room_id="R1", variable="co2", value=800.0,
        unit="ppm", state=EvidenceState.MEASURED,
        provenance=Provenance("sensor", "S1", instrument_id="S1", calibration_id="C1"),
        uncertainty=10.0,
    )
    with pytest.raises(ValueError, match="variable and unit"):
        Comparison.compare(predicted, measured)
