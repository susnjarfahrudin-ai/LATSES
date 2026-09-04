"""Link canonical Thermal room loads to canonical MEP HeatingZone records.

This module never creates rooms, walls, or a second heating model. It reads
thermal results from the canonical BuildingModel and updates the existing
BuildingModel-owned MEP registry by Room ID.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from lat_ces.building.mep import HeatingZone, ensure_mep_registry
from lat_ces.thermal.room_heat_loss import RoomHeatLossResult, calculate_room_heat_losses


@dataclass(frozen=True)
class HeatingZoneThermalLinkResult:
    zone_id: str
    room_id: str
    status: str
    room_heat_load_w: float | None
    findings: tuple[str, ...] = ()


def apply_thermal_room_loads_to_heating_zones(
    model: Any,
    *,
    design_indoor_c: float,
    design_outdoor_c: float,
) -> tuple[HeatingZoneThermalLinkResult, ...]:
    """Bind room-level Thermal heat loss to existing canonical HeatingZones.

    The only physical identity used for the link is ``HeatingZone.room_id``.
    Thermal remains authoritative for the calculated room transmission load;
    missing thermal inputs remain ``INPUT_REQUIRED``.
    """
    thermal_results = calculate_room_heat_losses(
        model,
        design_indoor_c=design_indoor_c,
        design_outdoor_c=design_outdoor_c,
    )
    thermal_by_room = {result.room_id: result for result in thermal_results}
    registry = ensure_mep_registry(model)
    results: list[HeatingZoneThermalLinkResult] = []

    for zone in registry.all_heating_zones:
        thermal: RoomHeatLossResult | None = thermal_by_room.get(zone.room_id)
        if thermal is None:
            results.append(
                HeatingZoneThermalLinkResult(
                    zone_id=zone.id,
                    room_id=zone.room_id,
                    status="INPUT_REQUIRED",
                    room_heat_load_w=None,
                    findings=("HeatingZone nema odgovarajući Room termički rezultat",),
                )
            )
            continue

        if thermal.status != "CALCULATED" or thermal.heat_loss_w is None:
            results.append(
                HeatingZoneThermalLinkResult(
                    zone_id=zone.id,
                    room_id=zone.room_id,
                    status="INPUT_REQUIRED",
                    room_heat_load_w=None,
                    findings=thermal.findings,
                )
            )
            continue

        registry.update_heating_zone(zone.id, room_heat_load_w=thermal.heat_loss_w)
        results.append(
            HeatingZoneThermalLinkResult(
                zone_id=zone.id,
                room_id=zone.room_id,
                status="CALCULATED",
                room_heat_load_w=thermal.heat_loss_w,
                findings=(),
            )
        )

    return tuple(results)


__all__ = [
    "HeatingZoneThermalLinkResult",
    "apply_thermal_room_loads_to_heating_zones",
]
