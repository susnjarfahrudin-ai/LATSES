"""Canonical MEP data and registry owned by the production BuildingModel."""
from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Dict, Iterable


@dataclass(frozen=True)
class VentilationOpening:
    id: str
    room_id: str
    kind: str
    diameter_m: float
    design_velocity_m_s: float = 0.05
    elevation_m: float = 0.70
    x_m: float = 0.0
    y_m: float = 0.0

    def __post_init__(self):
        if self.kind not in {"supply", "extract"}:
            raise ValueError("ventilation opening kind must be 'supply' or 'extract'")
        if self.diameter_m <= 0 or self.design_velocity_m_s <= 0 or self.elevation_m < 0:
            raise ValueError("ventilation opening dimensions must be positive")
        if self.x_m < 0 or self.y_m < 0:
            raise ValueError("ventilation opening plan coordinates cannot be negative")

    @property
    def area_m2(self) -> float:
        return 3.141592653589793 * self.diameter_m**2 / 4.0

    @property
    def design_flow_m3_s(self) -> float:
        return self.area_m2 * self.design_velocity_m_s

    @property
    def design_flow_m3_h(self) -> float:
        return self.design_flow_m3_s * 3600.0


@dataclass(frozen=True)
class WaterBranch:
    id: str
    room_id: str
    service: str
    diameter_m: float
    design_flow_m3_s: float
    length_m: float = 0.0
    x1_m: float = 0.0
    y1_m: float = 0.0
    x2_m: float = 0.0
    y2_m: float = 0.0

    def __post_init__(self):
        if self.service not in {"cold_water", "dhw", "return", "drain"}:
            raise ValueError("unsupported water service")
        if self.diameter_m <= 0 or self.design_flow_m3_s < 0 or self.length_m < 0:
            raise ValueError("invalid water branch dimensions")
        if min(self.x1_m, self.y1_m, self.x2_m, self.y2_m) < 0:
            raise ValueError("water branch plan coordinates cannot be negative")


@dataclass(frozen=True)
class HeatingZone:
    id: str
    room_id: str
    emitter_type: str
    design_supply_temp_c: float
    design_return_temp_c: float
    target_indoor_temp_c: float = 20.0
    room_heat_load_w: float | None = None
    mass_flow_kg_s: float | None = None

    def __post_init__(self):
        if self.emitter_type not in {"underfloor", "radiator", "wall", "ceiling", "convector", "air", "combined"}:
            raise ValueError("unsupported heating emitter")
        if self.design_supply_temp_c <= self.design_return_temp_c:
            raise ValueError("heating supply temperature must exceed return temperature")
        if self.room_heat_load_w is not None and self.room_heat_load_w <= 0:
            raise ValueError("room heat load must be positive when provided")
        if self.mass_flow_kg_s is not None and self.mass_flow_kg_s <= 0:
            raise ValueError("heating mass flow must be positive when provided")


def group_by_room(items: Iterable[object], attribute: str = "room_id") -> Dict[str, list]:
    grouped: Dict[str, list] = {}
    for item in items:
        room_id = getattr(item, attribute)
        grouped.setdefault(room_id, []).append(item)
    return grouped


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
