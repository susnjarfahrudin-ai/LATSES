"""Building-level MEP inputs attached to the canonical model.

Phase 1 keeps the objects deliberately small: they describe where an MEP
connection belongs and its design intent. Solvers remain separate so the same
objects can later be connected to the full LATCES network engines.
"""
from dataclasses import dataclass
from typing import Dict, Iterable


@dataclass(frozen=True)
class VentilationOpening:
    id: str
    room_id: str
    kind: str  # supply | extract
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
    service: str  # cold_water | dhw | return | drain
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
        if self.emitter_type not in {
            "underfloor", "radiator", "wall", "ceiling", "convector", "air", "combined"
        }:
            raise ValueError("unsupported heating emitter")
        if self.design_supply_temp_c <= self.design_return_temp_c:
            raise ValueError("heating supply temperature must exceed return temperature")
        if self.room_heat_load_w is not None and self.room_heat_load_w <= 0:
            raise ValueError("room heat load must be positive when provided")
        if self.mass_flow_kg_s is not None and self.mass_flow_kg_s <= 0:
            raise ValueError("heating mass flow must be positive when provided")
        if self.room_heat_load_w is None and self.mass_flow_kg_s is None:
            return
        if self.room_heat_load_w is not None and self.mass_flow_kg_s is not None:
            if self.room_heat_load_w <= 0 or self.mass_flow_kg_s <= 0:
                raise ValueError("heating load and mass flow must be positive")


def group_by_room(items: Iterable[object], attribute: str = "room_id") -> Dict[str, list]:
    grouped: Dict[str, list] = {}
    for item in items:
        room_id = getattr(item, attribute)
        grouped.setdefault(room_id, []).append(item)
    return grouped
