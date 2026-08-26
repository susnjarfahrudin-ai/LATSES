"""Read-only MEP views over BuildingModel-owned system objects.

MEP objects remain owned by the canonical Building Model. This adapter only
projects their identities and design data for engineering/reporting clients.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class MEPElementView:
    element_id: str
    room_id: str
    kind: str
    properties: tuple[tuple[str, object], ...]


@dataclass(frozen=True)
class MEPModelView:
    elements: tuple[MEPElementView, ...]

    def for_room(self, room_id: str) -> tuple[MEPElementView, ...]:
        return tuple(item for item in self.elements if item.room_id == room_id)


def _element_view(item: object) -> MEPElementView:
    element_id = getattr(item, "id")
    room_id = getattr(item, "room_id")
    kind = type(item).__name__
    names = {
        "VentilationOpening": ("kind", "diameter_m", "design_velocity_m_s", "elevation_m", "x_m", "y_m"),
        "WaterBranch": ("service", "diameter_m", "design_flow_m3_s", "length_m", "x1_m", "y1_m", "x2_m", "y2_m"),
        "HeatingZone": ("emitter_type", "design_supply_temp_c", "design_return_temp_c", "target_indoor_temp_c", "room_heat_load_w", "mass_flow_kg_s"),
    }
    properties = tuple((name, getattr(item, name)) for name in names.get(kind, ()))
    return MEPElementView(element_id, room_id, kind, properties)


def to_mep_view(elements: Iterable[object]) -> MEPModelView:
    """Create immutable read-only views without copying MEP ownership."""
    return MEPModelView(tuple(_element_view(item) for item in elements))
