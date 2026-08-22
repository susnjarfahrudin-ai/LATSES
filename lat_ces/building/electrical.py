"""Electrical design-intent layer owned by BuildingModel.

This is an input/accounting layer, not a protection or code-compliance solver.
Loads remain explicit so a later electrical standard engine can consume the same
BuildingModel without replacing the project data model.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from uuid import uuid4


@dataclass(frozen=True)
class ElectricalLoad:
    name: str
    kind: str
    room_id: str | None = None
    power_w: float = 0.0
    quantity: int = 1
    demand_factor: float = 1.0
    load_id: str = field(default_factory=lambda: f"EL-{uuid4()}")

    @property
    def connected_power_w(self) -> float:
        return max(0.0, self.power_w) * max(0, self.quantity)

    @property
    def demand_power_w(self) -> float:
        return self.connected_power_w * max(0.0, self.demand_factor)


@dataclass(frozen=True)
class ElectricalReport:
    status: str
    connected_power_w: float
    demand_power_w: float
    lighting_power_w: float
    socket_power_w: float
    equipment_power_w: float
    load_count: int
    findings: tuple[str, ...] = ()


class ElectricalRegistry:
    def __init__(self) -> None:
        self.loads: list[ElectricalLoad] = []

    def add(self, load: ElectricalLoad) -> ElectricalLoad:
        if load.power_w < 0 or load.quantity < 0:
            raise ValueError("Electrical load power and quantity must be >= 0")
        if not 0.0 <= load.demand_factor <= 1.0:
            raise ValueError("Electrical demand_factor must be between 0 and 1")
        self.loads.append(load)
        return load


def ensure_electrical_registry(model) -> ElectricalRegistry:
    registry = getattr(model, "electrical", None)
    if registry is None:
        registry = ElectricalRegistry()
        setattr(model, "electrical", registry)
    return registry


def calculate_electrical_report(model) -> ElectricalReport:
    registry = ensure_electrical_registry(model)
    findings: list[str] = []
    room_ids = {room.room_id for room in model.all_rooms()}
    for load in registry.loads:
        if not load.name.strip():
            findings.append("Electrical load without name")
        if load.room_id and load.room_id not in room_ids:
            findings.append(f"{load.name}: room_id nije pronađen u BuildingModel-u")

    connected = sum(load.connected_power_w for load in registry.loads)
    demand = sum(load.demand_power_w for load in registry.loads)
    lighting = sum(load.demand_power_w for load in registry.loads if load.kind.casefold() in {"light", "lighting", "rasvjeta"})
    sockets = sum(load.demand_power_w for load in registry.loads if load.kind.casefold() in {"socket", "outlet", "uticnica", "utičnica"})
    equipment = max(0.0, demand - lighting - sockets)

    status = "CALCULATED" if registry.loads and not findings else "INPUT_REQUIRED" if not registry.loads else "CHECK"
    report = ElectricalReport(
        status=status,
        connected_power_w=round(connected, 2),
        demand_power_w=round(demand, 2),
        lighting_power_w=round(lighting, 2),
        socket_power_w=round(sockets, 2),
        equipment_power_w=round(equipment, 2),
        load_count=len(registry.loads),
        findings=tuple(findings),
    )
    setattr(model, "electrical_report", report)
    return report


__all__ = ["ElectricalLoad", "ElectricalReport", "ElectricalRegistry", "ensure_electrical_registry", "calculate_electrical_report"]
