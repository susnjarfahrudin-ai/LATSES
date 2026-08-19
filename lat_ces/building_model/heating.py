"""First-order room heating load model.

Detailed transmission/thermal bridges and dynamic simulation remain adapters to
the existing LATCES thermal engines.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class HeatingResult:
    transmission_w: float
    ventilation_w: float
    internal_w: float
    required_w: float
    emitter_type: str


def calculate_heat_load(area_m2: float, volume_m3: float, delta_t_k: float, u_value_w_m2k: float, air_changes_per_hour: float, internal_gain_w: float = 0.0, emitter_type: str = "underfloor") -> HeatingResult:
    if min(area_m2, volume_m3, delta_t_k, u_value_w_m2k) <= 0:
        raise ValueError("area, volume, delta-T and U-value must be positive")
    if air_changes_per_hour < 0 or internal_gain_w < 0:
        raise ValueError("air changes and internal gain cannot be negative")
    transmission = area_m2 * u_value_w_m2k * delta_t_k
    ventilation = volume_m3 * air_changes_per_hour / 3600.0 * 1.2 * 1005.0 * delta_t_k
    required = max(0.0, transmission + ventilation - internal_gain_w)
    return HeatingResult(transmission, ventilation, internal_gain_w, required, emitter_type)


SUPPORTED_EMITTERS = (
    "underfloor", "radiator", "wall", "ceiling", "convector", "air", "combined"
)
