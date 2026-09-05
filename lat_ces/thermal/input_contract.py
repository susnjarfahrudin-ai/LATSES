"""Canonical thermal/MEP input contract.

This module contains data-only definitions. It does not perform engineering
calculations and has no dependency on email, Jira, GUI, or other adapters.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class CalculationScope(str, Enum):
    """Engineering scope selects which inputs are mandatory."""

    DESIGN_HEATING = "design_heating"
    DESIGN_COOLING = "design_cooling"
    HOURLY_DYNAMIC = "hourly_dynamic"
    MONTHLY_ENERGY = "monthly_energy"
    THERMAL_BRIDGE = "thermal_bridge"


class InputStatus(str, Enum):
    """Lifecycle state of a supplied input."""

    PRESENT = "PRESENT"
    MISSING = "MISSING"
    INVALID = "INVALID"
    UNVERIFIED = "UNVERIFIED"


@dataclass(frozen=True)
class MaterialThermalInput:
    """Thermal properties for one construction layer."""

    material_id: str
    thickness_m: Optional[float] = None
    conductivity_w_mk: Optional[float] = None
    density_kg_m3: Optional[float] = None
    heat_capacity_j_kgk: Optional[float] = None
    vapour_resistance_mu: Optional[float] = None
    source_ref: Optional[str] = None


@dataclass(frozen=True)
class TransparentElementInput:
    """Thermal/solar properties for a window, door or glazed element."""

    element_id: str
    area_m2: Optional[float] = None
    orientation_deg: Optional[float] = None
    tilt_deg: Optional[float] = None
    u_w_value_w_m2k: Optional[float] = None
    g_value: Optional[float] = None
    f_sh_ob: Optional[float] = None
    f_sh_w: Optional[float] = None
    source_ref: Optional[str] = None


@dataclass(frozen=True)
class ThermalBridgeInput:
    """Linear thermal bridge input with provenance."""

    bridge_id: str
    length_m: Optional[float] = None
    psi_value_w_mk: Optional[float] = None
    source_type: Optional[str] = None
    evidence_ref: Optional[str] = None


@dataclass(frozen=True)
class WeatherInput:
    """Weather inputs; one or both forms may be supplied depending on scope."""

    design_outdoor_temp_c: Optional[float] = None
    hourly_weather_ref: Optional[str] = None


@dataclass(frozen=True)
class IndoorConditionInput:
    """Zone design conditions."""

    design_indoor_temp_c: Optional[float] = None
    relative_humidity_pct: Optional[float] = None
    ventilation_ach: Optional[float] = None
    ventilation_flow_m3_h: Optional[float] = None


@dataclass(frozen=True)
class InternalGainsInput:
    """Internal gains as a static design value or named profile."""

    gains_w_m2: Optional[float] = None
    profile_ref: Optional[str] = None


@dataclass(frozen=True)
class ThermalZoneInput:
    """Complete input envelope for a thermal calculation scope."""

    zone_id: str
    scope: CalculationScope
    material_layers: List[MaterialThermalInput] = field(default_factory=list)
    transparent_elements: List[TransparentElementInput] = field(default_factory=list)
    thermal_bridges: List[ThermalBridgeInput] = field(default_factory=list)
    weather: WeatherInput = field(default_factory=WeatherInput)
    indoor: IndoorConditionInput = field(default_factory=IndoorConditionInput)
    internal_gains: InternalGainsInput = field(default_factory=InternalGainsInput)
    metadata: Dict[str, Any] = field(default_factory=dict)
