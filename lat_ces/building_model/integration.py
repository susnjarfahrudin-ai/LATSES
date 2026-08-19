"""Integrated engineering analysis for the small reference building.

The BuildingModel remains the single geometry source. MEP objects describe
explicit room-level inputs and the existing first-order engineering models
consume values derived from those objects.
"""
from dataclasses import dataclass
from typing import Dict, List

from .airflow import AirflowResult, calculate_airflow
from .core import BuildingModel
from .heating import HeatingResult, calculate_heat_load
from .systems import HeatingZone, VentilationOpening, WaterBranch, group_by_room
from .validation import ValidationResult, validate_model
from .water import WaterResult, calculate_water_flow


@dataclass(frozen=True)
class RoomEngineeringResult:
    room_id: str
    airflow: AirflowResult
    heating: HeatingResult


@dataclass(frozen=True)
class BuildingEngineeringReport:
    validation: List[ValidationResult]
    airflow: AirflowResult
    water: WaterResult
    heating: HeatingResult
    room_results: Dict[str, RoomEngineeringResult]
    ventilation_openings: List[VentilationOpening]
    water_branches: List[WaterBranch]
    heating_zones: List[HeatingZone]


def analyze_building(
    model: BuildingModel,
    *,
    ventilation_openings: List[VentilationOpening] | None = None,
    water_branches: List[WaterBranch] | None = None,
    heating_zones: List[HeatingZone] | None = None,
    airflow_ach: float = 0.85,
    airflow_velocity_m_s: float = 0.05,
    water_flow_m3_s: float = 0.0002,
    water_diameter_m: float = 0.02,
    outdoor_temp_c: float = -5.0,
    indoor_temp_c: float = 20.0,
    u_value_w_m2k: float = 0.30,
    emitter_type: str = "underfloor",
) -> BuildingEngineeringReport:
    """Run an integrated first engineering pass from one BuildingModel.

    Explicit MEP openings/branches/zones are inputs. If omitted, the function
    preserves the earlier first-order defaults, which keeps the API compatible.
    """
    if airflow_ach < 0:
        raise ValueError("airflow_ach cannot be negative")

    ventilation_openings = list(ventilation_openings or [])
    water_branches = list(water_branches or [])
    heating_zones = list(heating_zones or [])
    validation = validate_model(model)
    room_area = sum(room.floor_area_m2 for level in model.levels.values() for room in level.rooms.values())
    room_volume = model.total_volume_m3()
    if room_volume <= 0:
        raise ValueError("building must contain rooms with positive volume")

    # Use explicit ventilation openings when supplied; otherwise calculate the
    # equivalent opening needed for the requested ACH and low-velocity target.
    if ventilation_openings:
        total_flow_m3_s = sum(o.design_flow_m3_s for o in ventilation_openings)
        effective_area_m2 = sum(o.area_m2 for o in ventilation_openings)
        design_velocity = total_flow_m3_s / effective_area_m2
    else:
        total_flow_m3_s = room_volume * airflow_ach / 3600.0
        design_velocity = airflow_velocity_m_s
        effective_area_m2 = total_flow_m3_s / design_velocity if design_velocity > 0 else 0.0

    airflow = calculate_airflow(
        effective_area_m2,
        design_velocity,
        room_volume,
        target_velocity_m_s=0.05,
    )

    heating = calculate_heat_load(
        room_area,
        room_volume,
        indoor_temp_c - outdoor_temp_c,
        u_value_w_m2k,
        airflow.air_changes_per_hour,
        emitter_type=emitter_type,
    )
    water = calculate_water_flow(water_flow_m3_s, water_diameter_m)

    rooms = {
        room.id: room
        for level in model.levels.values()
        for room in level.rooms.values()
    }
    vents_by_room = group_by_room(ventilation_openings)
    zones_by_room = group_by_room(heating_zones)
    room_results: Dict[str, RoomEngineeringResult] = {}

    for room_id, room in rooms.items():
        vents = vents_by_room.get(room_id, [])
        if vents:
            area = sum(v.area_m2 for v in vents)
            velocity = sum(v.design_flow_m3_s for v in vents) / area
            room_airflow = calculate_airflow(area, velocity, room.volume_m3, target_velocity_m_s=0.05)
        else:
            room_flow = room.volume_m3 * airflow_ach / 3600.0
            area = room_flow / airflow_velocity_m_s if airflow_velocity_m_s > 0 else 0.0
            room_airflow = calculate_airflow(area, airflow_velocity_m_s, room.volume_m3, target_velocity_m_s=0.05)

        zone = zones_by_room.get(room_id, [None])[0]
        room_emitter = zone.emitter_type if zone else emitter_type
        room_heating = calculate_heat_load(
            room.floor_area_m2,
            room.volume_m3,
            indoor_temp_c - outdoor_temp_c,
            u_value_w_m2k,
            room_airflow.air_changes_per_hour,
            emitter_type=room_emitter,
        )
        room_results[room_id] = RoomEngineeringResult(room_id, room_airflow, room_heating)

    return BuildingEngineeringReport(
        validation=validation,
        airflow=airflow,
        water=water,
        heating=heating,
        room_results=room_results,
        ventilation_openings=ventilation_openings,
        water_branches=water_branches,
        heating_zones=heating_zones,
    )
