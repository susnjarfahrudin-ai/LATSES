"""Airflow calculations for the unified building model."""
from dataclasses import dataclass
from math import sqrt


@dataclass(frozen=True)
class AirflowResult:
    flow_m3_s: float
    flow_m3_h: float
    velocity_m_s: float
    air_changes_per_hour: float
    human_zone_ok: bool


def calculate_airflow(area_m2: float, velocity_m_s: float, room_volume_m3: float, target_velocity_m_s: float = 0.05) -> AirflowResult:
    if area_m2 <= 0 or velocity_m_s < 0 or room_volume_m3 <= 0:
        raise ValueError("area, velocity and room volume must be valid")
    flow = area_m2 * velocity_m_s
    return AirflowResult(
        flow_m3_s=flow,
        flow_m3_h=flow * 3600.0,
        velocity_m_s=velocity_m_s,
        air_changes_per_hour=flow * 3600.0 / room_volume_m3,
        human_zone_ok=velocity_m_s <= target_velocity_m_s,
    )


def stack_effect_velocity(height_m: float, indoor_temp_c: float, outdoor_temp_c: float, discharge_coefficient: float = 0.65) -> float:
    """First-order buoyancy estimate; wind and network resistance require a full solver."""
    if height_m <= 0 or discharge_coefficient <= 0:
        raise ValueError("height and discharge coefficient must be positive")
    if indoor_temp_c <= -273.15 or outdoor_temp_c <= -273.15:
        raise ValueError("temperature below absolute zero")
    if abs(indoor_temp_c - outdoor_temp_c) < 1e-12:
        return 0.0
    t_in = indoor_temp_c + 273.15
    t_out = outdoor_temp_c + 273.15
    g = 9.80665
    return discharge_coefficient * sqrt(2.0 * g * height_m * abs(t_in - t_out) / t_in)
