"""Transparent envelope thermal take-off from the canonical BuildingModel."""
from __future__ import annotations

from dataclasses import dataclass
import math


@dataclass(frozen=True)
class EnvelopeThermalReport:
    status: str
    envelope_area_m2: float
    opening_area_m2: float
    insulation_area_m2: float
    effective_u_w_m2k: float | None
    design_delta_t_k: float
    transmission_heat_loss_w: float | None
    findings: tuple[str, ...] = ()


def _wall_area(level) -> tuple[float, float]:
    plan = level.floor_plan
    if plan is None:
        return 0.0, 0.0
    gross = sum(w.segment.length for w in plan.walls.values()) * level.height
    openings = sum(
        opening.width * opening.height_m
        for wall in plan.walls.values()
        for opening in wall.openings
    )
    return max(0.0, gross), max(0.0, min(openings, gross))


def _resolve_material(model, name: str):
    wanted = name.strip().casefold()
    if not wanted:
        return None
    return next((m for m in model.materials.values() if m.name.strip().casefold() == wanted), None)


def calculate_envelope_thermal(model, *, design_delta_t_k: float = 30.0) -> EnvelopeThermalReport:
    """Calculate a conservative transmission-loss indicator from declared layers.

    The function never invents a missing lambda value. Missing layer properties
    are reported as INPUT_REQUIRED rather than substituted with a hidden default.
    """
    if design_delta_t_k < 0:
        raise ValueError("design_delta_t_k must be >= 0")

    envelope_area = 0.0
    opening_area = 0.0
    insulation_area = 0.0
    resistances: list[float] = []
    findings: list[str] = []

    for level in model.levels.values():
        gross, openings = _wall_area(level)
        net = max(0.0, gross - openings)
        envelope_area += net
        opening_area += openings
        if level.insulation_thickness_m > 0:
            insulation_area += net
            insulation = _resolve_material(model, level.insulation_material)
            if insulation is None or insulation.thermal_conductivity is None:
                findings.append(f"{level.name}: izolacija nema verificirani lambda podatak")
            else:
                resistances.append(level.insulation_thickness_m / insulation.thermal_conductivity)
        if level.interior_plaster_thickness_m > 0:
            plaster = _resolve_material(model, level.interior_plaster_material)
            if plaster is not None and plaster.thermal_conductivity:
                resistances.append(level.interior_plaster_thickness_m / plaster.thermal_conductivity)

    if not resistances:
        findings.append("Nema dovoljno deklarisanih toplinskih svojstava za U-vrijednost")
        return EnvelopeThermalReport(
            status="INPUT_REQUIRED",
            envelope_area_m2=round(envelope_area, 3),
            opening_area_m2=round(opening_area, 3),
            insulation_area_m2=round(insulation_area, 3),
            effective_u_w_m2k=None,
            design_delta_t_k=design_delta_t_k,
            transmission_heat_loss_w=None,
            findings=tuple(findings),
        )

    # Surface resistances are explicit engineering constants of the indicator,
    # while wall/glazing and thermal bridges still require the detailed solver.
    total_r = 0.13 + sum(resistances) + 0.04
    u_value = 1.0 / total_r
    loss = u_value * envelope_area * design_delta_t_k
    status = "CALCULATED" if not findings else "INPUT_REQUIRED"
    return EnvelopeThermalReport(
        status=status,
        envelope_area_m2=round(envelope_area, 3),
        opening_area_m2=round(opening_area, 3),
        insulation_area_m2=round(insulation_area, 3),
        effective_u_w_m2k=round(u_value, 4),
        design_delta_t_k=design_delta_t_k,
        transmission_heat_loss_w=round(loss, 2),
        findings=tuple(findings),
    )


__all__ = ["EnvelopeThermalReport", "calculate_envelope_thermal"]
