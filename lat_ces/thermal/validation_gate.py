"""Scope-aware validation gate for thermal/MEP inputs.

The gate is deterministic and side-effect free. It decides whether a specific
calculation scope has sufficient inputs; it does not guess missing values.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from .input_contract import CalculationScope, InputStatus, ThermalZoneInput


@dataclass(frozen=True)
class MissingParameter:
    category: str
    element_id: str
    field: str
    expected_unit: str
    responsible_role: str
    hint: str


@dataclass(frozen=True)
class ValidationResult:
    status: InputStatus
    calculation_allowed: bool
    scope: CalculationScope
    missing_parameters: List[MissingParameter] = field(default_factory=list)
    invalid_parameters: List[MissingParameter] = field(default_factory=list)
    unverified_parameters: List[MissingParameter] = field(default_factory=list)


def _missing(category: str, element_id: str, field: str, unit: str, role: str, hint: str) -> MissingParameter:
    return MissingParameter(category, element_id, field, unit, role, hint)


def validate_thermal_inputs(inputs: ThermalZoneInput) -> ValidationResult:
    """Validate inputs required for the selected engineering scope."""
    missing: List[MissingParameter] = []
    invalid: List[MissingParameter] = []
    unverified: List[MissingParameter] = []

    for layer in inputs.material_layers:
        required = (
            ("thickness_m", layer.thickness_m, "m", "Arhitektura / Građevina"),
            ("conductivity_w_mk", layer.conductivity_w_mk, "W/mK", "Arhitektura / Proizvođač"),
            ("density_kg_m3", layer.density_kg_m3, "kg/m³", "Arhitektura / Građevina"),
            ("heat_capacity_j_kgk", layer.heat_capacity_j_kgk, "J/kgK", "Arhitektura / Građevina"),
        )
        for field_name, value, unit, role in required:
            if value is None:
                missing.append(_missing("material_layers", layer.material_id, field_name, unit, role, "Unesite deklarisanu vrijednost."))
            elif value <= 0:
                invalid.append(_missing("material_layers", layer.material_id, field_name, unit, role, "Vrijednost mora biti pozitivna."))
        if inputs.scope in {CalculationScope.HOURLY_DYNAMIC, CalculationScope.MONTHLY_ENERGY} and layer.source_ref is None:
            unverified.append(_missing("material_layers", layer.material_id, "source_ref", "ref", "Arhitektura / Građevina", "Navedite izvor materijalnih podataka."))

    for element in inputs.transparent_elements:
        required = (
            ("area_m2", element.area_m2, "m²", "Arhitektura"),
            ("orientation_deg", element.orientation_deg, "°", "Arhitektura"),
            ("tilt_deg", element.tilt_deg, "°", "Arhitektura"),
            ("u_w_value_w_m2k", element.u_w_value_w_m2k, "W/m²K", "Arhitektura / Proizvođač"),
            ("g_value", element.g_value, "-", "Arhitektura / Proizvođač stakla"),
            ("f_sh_ob", element.f_sh_ob, "-", "Arhitektura / MEP"),
            ("f_sh_w", element.f_sh_w, "-", "Arhitektura / MEP"),
        )
        for field_name, value, unit, role in required:
            if value is None:
                missing.append(_missing("transparent_elements", element.element_id, field_name, unit, role, "Unesite tehničku vrijednost transparentnog elementa."))
        if element.orientation_deg is not None and not 0 <= element.orientation_deg <= 360:
            invalid.append(_missing("transparent_elements", element.element_id, "orientation_deg", "°", "Arhitektura", "Dozvoljeni raspon je 0–360°."))
        if element.tilt_deg is not None and not 0 <= element.tilt_deg <= 180:
            invalid.append(_missing("transparent_elements", element.element_id, "tilt_deg", "°", "Arhitektura", "Dozvoljeni raspon je 0–180°."))

    for bridge in inputs.thermal_bridges:
        if inputs.scope == CalculationScope.THERMAL_BRIDGE or bridge.psi_value_w_mk is not None or bridge.length_m is not None:
            if bridge.length_m is None:
                missing.append(_missing("thermal_bridges", bridge.bridge_id, "length_m", "m", "Arhitektura / Građevinska Fizika", "Unesite dužinu termičkog mosta."))
            if bridge.psi_value_w_mk is None:
                missing.append(_missing("thermal_bridges", bridge.bridge_id, "psi_value_w_mk", "W/mK", "Arhitektura / Građevinska Fizika", "Navedite Ψ iz odgovarajućeg detaljnog proračuna ili provjerenog izvora."))
            if bridge.psi_value_w_mk is not None and bridge.source_type is None:
                unverified.append(_missing("thermal_bridges", bridge.bridge_id, "source_type", "ref", "Arhitektura / Građevinska Fizika", "Navedite porijeklo Ψ vrijednosti."))

    if inputs.indoor.design_indoor_temp_c is None:
        missing.append(_missing("indoor", inputs.zone_id, "design_indoor_temp_c", "°C", "MEP Inženjer / Tehnolog", "Unesite projektnu unutrašnju temperaturu."))

    if inputs.indoor.ventilation_ach is None and inputs.indoor.ventilation_flow_m3_h is None:
        missing.append(_missing("indoor", inputs.zone_id, "ventilation", "1/h or m³/h", "MEP Inženjer", "Unesite projektni ventilacioni protok ili broj izmjena vazduha."))

    if inputs.scope in {CalculationScope.HOURLY_DYNAMIC, CalculationScope.MONTHLY_ENERGY}:
        if inputs.weather.hourly_weather_ref is None:
            missing.append(_missing("weather", inputs.zone_id, "hourly_weather_ref", "ref", "MEP Inženjer", "Navedite klimatsku datoteku ili validirani weather source."))
    elif inputs.weather.design_outdoor_temp_c is None:
        missing.append(_missing("weather", inputs.zone_id, "design_outdoor_temp_c", "°C", "MEP Inženjer", "Unesite projektnu vanjsku temperaturu."))

    if inputs.internal_gains.gains_w_m2 is None and inputs.internal_gains.profile_ref is None:
        missing.append(_missing("internal_gains", inputs.zone_id, "internal_gains", "W/m² or profile", "Investitor / Elektro / Tehnolog", "Unesite unutrašnje dobitke ili referencu profila."))

    if invalid:
        status = InputStatus.INVALID
    elif missing:
        status = InputStatus.MISSING
    elif unverified:
        status = InputStatus.UNVERIFIED
    else:
        status = InputStatus.PRESENT

    return ValidationResult(
        status=status,
        calculation_allowed=status == InputStatus.PRESENT,
        scope=inputs.scope,
        missing_parameters=missing,
        invalid_parameters=invalid,
        unverified_parameters=unverified,
    )
