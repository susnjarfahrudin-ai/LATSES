from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Callable

from lat_ces.scientific.evidence.property_instance import PropertyInstance


@dataclass(frozen=True)
class CalculationContext:
    """Context in which one engineering property may be admitted."""

    context_id: str
    property_id: str
    subject_id: str
    unit: str
    purpose: str

    def __post_init__(self) -> None:
        for name in ("context_id", "property_id", "subject_id", "unit", "purpose"):
            if not getattr(self, name).strip():
                raise ValueError(f"calculation context {name} must be non-empty")


@dataclass(frozen=True)
class Admission:
    """Context-bound computational admission; not a verification record."""

    property_instance: PropertyInstance
    context: CalculationContext
    status: str
    reason: str = ""


@dataclass(frozen=True)
class ThermalCalculationResult:
    """Result with explicit lineage back to the admitted property."""

    u_value_w_m2k: float
    heat_loss_w: float
    property_id: str
    subject_id: str
    context_id: str
    formula: str


def admit_thermal_conductivity(
    instance: PropertyInstance,
    context: CalculationContext,
    *,
    validator: Callable[[float], bool] | None = None,
) -> Admission:
    """Admit exactly one thermal-conductivity instance for one context."""
    if instance.property_id != context.property_id:
        return Admission(instance, context, "REJECTED", "property identity mismatch")
    if instance.subject_id != context.subject_id:
        return Admission(instance, context, "REJECTED", "subject identity mismatch")
    if instance.unit != context.unit:
        return Admission(instance, context, "REJECTED", "unit mismatch")
    if not isinstance(instance.value, (int, float)) or isinstance(instance.value, bool):
        return Admission(instance, context, "REJECTED", "thermal conductivity must be numeric")
    if not isfinite(float(instance.value)) or float(instance.value) <= 0:
        return Admission(instance, context, "REJECTED", "thermal conductivity must be finite and positive")
    if validator is not None and not validator(float(instance.value)):
        return Admission(instance, context, "REJECTED", "property validation failed")
    return Admission(instance, context, "ACCEPTED_FOR_CALCULATION")


def calculate_admitted_wall_heat_loss(
    admission: Admission,
    *,
    area_m2: float,
    thickness_m: float,
    delta_t_k: float,
    r_si_m2k_w: float,
    r_se_m2k_w: float,
) -> ThermalCalculationResult:
    """Use only the admitted property instance in the thermal formula.

    This function is the Consumer Authority Point for this isolated vertical:
    the admitted thermal-conductivity value enters the mathematical formula
    here and is carried into the resulting lineage.
    """
    if admission.status != "ACCEPTED_FOR_CALCULATION":
        raise ValueError("property instance is not admitted for this calculation context")
    if min(area_m2, thickness_m, delta_t_k, r_si_m2k_w) <= 0 or r_se_m2k_w < 0:
        raise ValueError("thermal calculation inputs must be physically positive/non-negative")

    conductivity = float(admission.property_instance.value)
    resistance = r_si_m2k_w + thickness_m / conductivity + r_se_m2k_w
    u_value = 1.0 / resistance
    heat_loss = u_value * area_m2 * delta_t_k
    return ThermalCalculationResult(
        u_value_w_m2k=u_value,
        heat_loss_w=heat_loss,
        property_id=admission.property_instance.property_id,
        subject_id=admission.property_instance.subject_id,
        context_id=admission.context.context_id,
        formula="U=1/(Rsi+d/lambda+Rse); Q=U*A*DeltaT",
    )


__all__ = [
    "Admission",
    "CalculationContext",
    "ThermalCalculationResult",
    "admit_thermal_conductivity",
    "calculate_admitted_wall_heat_loss",
]
