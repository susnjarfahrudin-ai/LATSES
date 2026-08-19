"""Runtime MEP registry attached to the canonical GUI BuildingModel.

The registry keeps MEP objects out of GUI widgets and makes them explicit
BuildingModel-owned data. Each editor slice owns CRUD here; engineering
solvers remain downstream consumers of the same objects.
"""
from __future__ import annotations

from dataclasses import replace
from typing import Dict

from lat_ces.building_model.systems import HeatingZone, VentilationOpening, WaterBranch


class MEPRegistry:
    """Mutable registry owned by one BuildingModel instance."""

    def __init__(self) -> None:
        self.ventilation_openings: Dict[str, VentilationOpening] = {}
        self.water_branches: Dict[str, WaterBranch] = {}
        self.heating_zones: Dict[str, HeatingZone] = {}

    @property
    def all_ventilation_openings(self) -> tuple[VentilationOpening, ...]:
        return tuple(self.ventilation_openings.values())

    @property
    def all_water_branches(self) -> tuple[WaterBranch, ...]:
        return tuple(self.water_branches.values())

    @property
    def all_heating_zones(self) -> tuple[HeatingZone, ...]:
        return tuple(self.heating_zones.values())

    def add_ventilation_opening(self, opening: VentilationOpening) -> VentilationOpening:
        if opening.id in self.ventilation_openings:
            raise ValueError(f"Duplicate ventilation opening id: {opening.id}")
        self.ventilation_openings[opening.id] = opening
        return opening

    def update_ventilation_opening(self, opening_id: str, **changes: object) -> VentilationOpening:
        current = self.ventilation_openings[opening_id]
        updated = replace(current, **changes)
        self.ventilation_openings[opening_id] = updated
        return updated

    def remove_ventilation_opening(self, opening_id: str) -> VentilationOpening:
        return self.ventilation_openings.pop(opening_id)

    def add_water_branch(self, branch: WaterBranch) -> WaterBranch:
        if branch.id in self.water_branches:
            raise ValueError(f"Duplicate water branch id: {branch.id}")
        self.water_branches[branch.id] = branch
        return branch

    def update_water_branch(self, branch_id: str, **changes: object) -> WaterBranch:
        current = self.water_branches[branch_id]
        updated = replace(current, **changes)
        self.water_branches[branch_id] = updated
        return updated

    def remove_water_branch(self, branch_id: str) -> WaterBranch:
        return self.water_branches.pop(branch_id)

    def add_heating_zone(self, zone: HeatingZone) -> HeatingZone:
        if zone.id in self.heating_zones:
            raise ValueError(f"Duplicate heating zone id: {zone.id}")
        self.heating_zones[zone.id] = zone
        return zone

    def update_heating_zone(self, zone_id: str, **changes: object) -> HeatingZone:
        current = self.heating_zones[zone_id]
        updated = replace(current, **changes)
        self.heating_zones[zone_id] = updated
        return updated

    def remove_heating_zone(self, zone_id: str) -> HeatingZone:
        return self.heating_zones.pop(zone_id)


def ensure_mep_registry(model: object) -> MEPRegistry:
    """Attach and return exactly one MEP registry for a BuildingModel instance."""
    registry = getattr(model, "mep", None)
    if registry is None:
        registry = MEPRegistry()
        setattr(model, "mep", registry)
    if not isinstance(registry, MEPRegistry):
        raise TypeError("BuildingModel.mep must be an MEPRegistry")
    return registry
