import pytest

from lat_ces.building.geometry import Box3D, Point3D
from lat_ces.building.reference_house_project import build_reference_house_workflow
from lat_ces.scientific.core.performance_state import (
    BuildingPerformanceState,
    EvidenceState,
    Provenance,
    Comparison,
)
from lat_ces.scientific.iaq import IAQModel
from lat_ces.scientific.measurement import AccuracySpec, MeasurementDevice
from lat_ces.scientific.room_dynamics import RoomDynamicsModel
from lat_ces.scientific.units.core import DIMENSIONLESS, celsius, Unit


def _reference_room():
    workflow = build_reference_house_workflow()
    level = next(iter(workflow.model.levels.values()))
    room = level.add_room(
        __import__("lat_ces.building.model", fromlist=["Room"]).Room(
            name="Reference Room",
            footprint=Box3D(Point3D(0.0, 0.0, level.elevation), 5.0, 4.0, level.height),
        )
    )
    return workflow, level, room


def _measurement_device(name, unit, min_range, max_range, calibration_offset):
    return MeasurementDevice(
        name=name,
        device_type="calibrated reference instrument",
        unit=unit,
        accuracy_spec=AccuracySpec(relative_error=0.001, absolute_error=0.01),
        min_range=min_range,
        max_range=max_range,
        calibration_offset=calibration_offset,
        sko_uuid=f"CAL-{name}",
    )


def test_reference_house_temperature_and_co2_end_to_end_validation():
    workflow, level, room = _reference_room()
    state = BuildingPerformanceState(workflow.model)

    temperature_model = RoomDynamicsModel(room.volume, thermal_mass_kJ_K=500.0)
    simulated_temperature = temperature_model.compute_next_temperature(
        current_temp=20.0, heat_gain_w=1000.0, time_step_s=60.0
    )

    co2_model = IAQModel(room.volume, base_outdoor_co2=400.0)
    simulated_co2 = co2_model.update_co2_concentration(
        current_co2=400.0, fresh_air_flow=0.05, occupants=1, dt_seconds=60.0
    )

    simulated_temperature_observation = state.observation(
        level_id=level.level_id,
        room_id=room.room_id,
        variable="temperature",
        value=simulated_temperature,
        unit="°C",
        state=EvidenceState.SIMULATED,
        provenance=Provenance(
            source="RoomDynamicsModel",
            source_id="room-dynamics-reference-house",
            model_revision="current",
        ),
        uncertainty=0.05,
    )
    simulated_co2_observation = state.observation(
        level_id=level.level_id,
        room_id=room.room_id,
        variable="CO2",
        value=simulated_co2,
        unit="ppm",
        state=EvidenceState.SIMULATED,
        provenance=Provenance(
            source="IAQModel",
            source_id="iaq-reference-house",
            model_revision="current",
        ),
        uncertainty=2.0,
    )

    temperature_device = _measurement_device(
        "TEMP-REF-01", celsius, -20.0, 80.0, calibration_offset=0.02
    )
    co2_unit = Unit("parts per million", "ppm", DIMENSIONLESS)
    co2_device = _measurement_device(
        "CO2-REF-01", co2_unit, 300.0, 5000.0, calibration_offset=0.2
    )

    measured_temperature = temperature_device.measure(simulated_temperature + 0.06)
    measured_co2 = co2_device.measure(simulated_co2 + 0.5)

    measured_temperature_observation = state.observation(
        level_id=level.level_id,
        room_id=room.room_id,
        variable="temperature",
        value=measured_temperature.value,
        unit="°C",
        state=EvidenceState.MEASURED,
        provenance=Provenance(
            source="MeasurementDevice",
            source_id=temperature_device.uuid,
            instrument_id=temperature_device.uuid,
            calibration_id="CAL-TEMP-REF-01",
            timestamp="2026-08-20T21:00:00+02:00",
        ),
        uncertainty=measured_temperature.uncertainty,
    )
    measured_co2_observation = state.observation(
        level_id=level.level_id,
        room_id=room.room_id,
        variable="CO2",
        value=measured_co2.value,
        unit="ppm",
        state=EvidenceState.MEASURED,
        provenance=Provenance(
            source="MeasurementDevice",
            source_id=co2_device.uuid,
            instrument_id=co2_device.uuid,
            calibration_id="CAL-CO2-REF-01",
            timestamp="2026-08-20T21:00:00+02:00",
        ),
        uncertainty=measured_co2.uncertainty,
    )

    temperature_comparison = Comparison.compare(
        simulated_temperature_observation, measured_temperature_observation
    )
    co2_comparison = Comparison.compare(
        simulated_co2_observation, measured_co2_observation
    )

    assert simulated_temperature_observation.state is EvidenceState.SIMULATED
    assert simulated_co2_observation.state is EvidenceState.SIMULATED
    assert measured_temperature_observation.state is EvidenceState.MEASURED
    assert measured_co2_observation.state is EvidenceState.MEASURED
    assert measured_temperature_observation.provenance.calibration_id == "CAL-TEMP-REF-01"
    assert measured_co2_observation.provenance.calibration_id == "CAL-CO2-REF-01"
    assert temperature_comparison.residual == pytest.approx(0.04)
    assert co2_comparison.residual == pytest.approx(0.3)
    assert temperature_comparison.validate(0.1) is EvidenceState.VALIDATED
    assert co2_comparison.validate(1.0) is EvidenceState.VALIDATED


def test_reference_house_simulation_without_measurement_is_unknown():
    workflow, level, room = _reference_room()
    state = BuildingPerformanceState(workflow.model)
    predicted = state.observation(
        level_id=level.level_id,
        room_id=room.room_id,
        variable="temperature",
        value=21.0,
        unit="°C",
        state=EvidenceState.SIMULATED,
        provenance=Provenance(
            source="RoomDynamicsModel",
            source_id="reference-house-no-measurement",
        ),
        uncertainty=0.1,
    )

    comparison = Comparison.compare(predicted, None)

    assert comparison.status is EvidenceState.UNKNOWN
    assert comparison.validate(0.5) is EvidenceState.UNKNOWN
