"""Canonical MEP data and registry owned by the production BuildingModel."""
from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Dict, Iterable


HEATING_SOURCES = (
    "heat_pump_air_water",
    "heat_pump_air_air",
    "ground_source_heat_pump",
    "water_source_heat_pump",
    "gas_boiler",
    "oil_boiler",
    "pellet_boiler",
    "pellet_stove",
    "wood_biomass_boiler",
    "district_heating",
    "electric_boiler",
    "electric_direct",
    "infrared",
    "solar_thermal",
    "hybrid",
)

HEATING_EMITTERS = (
    "underfloor",
    "radiator",
    "fan_coil",
    "air_conditioner",
    "wall_heating",
    "ceiling_heating",
    "convector",
    "electric_panel",
    "infrared_panel",
    "heated_towel_rail",
    "air",
    "combined",
)


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
    source_type: str = "heat_pump_air_water"
    source_product_id: str | None = None
    emitter_product_id: str | None = None
    target_indoor_temp_c: float = 20.0
    room_heat_load_w: float | None = None
    mass_flow_kg_s: float | None = None

    def __post_init__(self):
        if self.emitter_type not in HEATING_EMITTERS:
            raise ValueError(f"unsupported heating emitter: {self.emitter_type}")
        if self.source_type not in HEATING_SOURCES:
            raise ValueError(f"unsupported heating source: {self.source_type}")
        if self.design_supply_temp_c <= self.design_return_temp_c:
            raise ValueError("heating supply temperature must exceed return temperature")
        if self.room_heat_load_w is not None and self.room_heat_load_w <= 0:
            raise ValueError("room heat load must be positive when provided")
        if self.mass_flow_kg_s is not None and self.mass_flow_kg_s <= 0:
            raise ValueError("heating mass flow must be positive when provided")


@dataclass(frozen=True)
class UnderfloorHeatingCircuit:
    """One canonical floor-heating circuit represented by 3D path points."""

    id: str
    room_id: str
    level_id: str
    pipe_product_id: str
    spacing_m: float
    path_points_m: tuple[tuple[float, float, float], ...] = ()
    length_m: float | None = None
    design_supply_temp_c: float = 35.0
    design_return_temp_c: float = 30.0
    design_flow_l_min: float | None = None

    def __post_init__(self):
        if not self.pipe_product_id.strip():
            raise ValueError("pipe_product_id is required")
        if self.spacing_m <= 0:
            raise ValueError("floor-heating pipe spacing must be > 0")
        if self.design_supply_temp_c <= self.design_return_temp_c:
            raise ValueError("floor-heating supply temperature must exceed return temperature")
        for point in self.path_points_m:
            if len(point) != 3 or any(value < 0 for value in point):
                raise ValueError("floor-heating path points must be non-negative 3D coordinates")
        if self.length_m is not None and self.length_m <= 0:
            raise ValueError("floor-heating circuit length must be positive when provided")
        if self.design_flow_l_min is not None and self.design_flow_l_min <= 0:
            raise ValueError("floor-heating circuit design flow must be positive when provided")


@dataclass(frozen=True)
class UnderfloorHeatingSystem:
    """Room/level assembly; identity links refer to catalog products."""

    id: str
    room_id: str
    level_id: str
    pipe_product_id: str
    pipe_spacing_m: float
    insulation_product_id: str | None = None
    insulation_thickness_m: float | None = None
    slab_material_id: str | None = None
    screed_product_id: str | None = None
    screed_thickness_m: float | None = None
    finish_product_id: str | None = None
    finish_thickness_m: float | None = None
    source_type: str = "heat_pump_air_water"
    source_product_id: str | None = None
    target_indoor_temp_c: float = 20.0
    design_supply_temp_c: float = 35.0
    design_return_temp_c: float = 30.0
    target_floor_surface_temp_c: float | None = None
    required_heat_w: float | None = None
    heat_output_w_m2: float | None = None

    def __post_init__(self):
        if not self.pipe_product_id.strip():
            raise ValueError("pipe_product_id is required")
        if self.pipe_spacing_m <= 0:
            raise ValueError("floor-heating pipe spacing must be > 0")
        if self.source_type not in HEATING_SOURCES:
            raise ValueError(f"unsupported heating source: {self.source_type}")
        if self.design_supply_temp_c <= self.design_return_temp_c:
            raise ValueError("floor-heating supply temperature must exceed return temperature")
        for name, value in (
            ("insulation_thickness_m", self.insulation_thickness_m),
            ("screed_thickness_m", self.screed_thickness_m),
            ("finish_thickness_m", self.finish_thickness_m),
        ):
            if value is not None and value <= 0:
                raise ValueError(f"{name} must be positive when provided")
        for name, value in (
            ("target_floor_surface_temp_c", self.target_floor_surface_temp_c),
            ("required_heat_w", self.required_heat_w),
            ("heat_output_w_m2", self.heat_output_w_m2),
        ):
            if value is not None and value <= 0:
                raise ValueError(f"{name} must be positive when provided")


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
        self.underfloor_systems: Dict[str, UnderfloorHeatingSystem] = {}
        self.underfloor_circuits: Dict[str, UnderfloorHeatingCircuit] = {}

    @property
    def all_ventilation_openings(self) -> tuple[VentilationOpening, ...]:
        return tuple(self.ventilation_openings.values())

    @property
    def all_water_branches(self) -> tuple[WaterBranch, ...]:
        return tuple(self.water_branches.values())

    @property
    def all_heating_zones(self) -> tuple[HeatingZone, ...]:
        return tuple(self.heating_zones.values())

    @property
    def all_underfloor_systems(self) -> tuple[UnderfloorHeatingSystem, ...]:
        return tuple(self.underfloor_systems.values())

    @property
    def all_underfloor_circuits(self) -> tuple[UnderfloorHeatingCircuit, ...]:
        return tuple(self.underfloor_circuits.values())

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

    def add_underfloor_system(self, system: UnderfloorHeatingSystem) -> UnderfloorHeatingSystem:
        if system.id in self.underfloor_systems:
            raise ValueError(f"Duplicate underfloor system id: {system.id}")
        self.underfloor_systems[system.id] = system
        return system

    def update_underfloor_system(self, system_id: str, **changes: object) -> UnderfloorHeatingSystem:
        current = self.underfloor_systems[system_id]
        updated = replace(current, **changes)
        self.underfloor_systems[system_id] = updated
        return updated

    def remove_underfloor_system(self, system_id: str) -> UnderfloorHeatingSystem:
        return self.underfloor_systems.pop(system_id)

    def add_underfloor_circuit(self, circuit: UnderfloorHeatingCircuit) -> UnderfloorHeatingCircuit:
        if circuit.id in self.underfloor_circuits:
            raise ValueError(f"Duplicate underfloor circuit id: {circuit.id}")
        self.underfloor_circuits[circuit.id] = circuit
        return circuit

    def update_underfloor_circuit(self, circuit_id: str, **changes: object) -> UnderfloorHeatingCircuit:
        current = self.underfloor_circuits[circuit_id]
        updated = replace(current, **changes)
        self.underfloor_circuits[circuit_id] = updated
        return updated

    def remove_underfloor_circuit(self, circuit_id: str) -> UnderfloorHeatingCircuit:
        return self.underfloor_circuits.pop(circuit_id)


def ensure_mep_registry(model: object) -> MEPRegistry:
    """Attach and return exactly one MEP registry for a BuildingModel instance."""
    registry = getattr(model, "mep", None)
    if registry is None:
        registry = MEPRegistry()
        setattr(model, "mep", registry)
    if not isinstance(registry, MEPRegistry):
        raise TypeError("BuildingModel.mep must be an MEPRegistry")
    return registry


__all__ = [
    "HEATING_SOURCES",
    "HEATING_EMITTERS",
    "VentilationOpening",
    "WaterBranch",
    "HeatingZone",
    "UnderfloorHeatingCircuit",
    "UnderfloorHeatingSystem",
    "MEPRegistry",
    "ensure_mep_registry",
]
