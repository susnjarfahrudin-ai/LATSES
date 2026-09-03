"""First-class building elements owned by the canonical BuildingModel."""
from __future__ import annotations

from dataclasses import dataclass, field

from .geometry import Box3D


def _id(prefix: str, name: str) -> str:
    safe = "".join(ch if ch.isalnum() else "-" for ch in name.lower()).strip("-") or "element"
    return f"{prefix}:{safe}"


@dataclass(frozen=True)
class Stair:
    """Canonical stair geometry and construction parameters."""

    name: str
    footprint: Box3D
    riser_count: int | None = None
    riser_height_m: float | None = None
    tread_width_m: float | None = None
    landing: bool = False
    railing: bool = False
    floor_opening: bool = False
    material_id: str | None = None
    id: str = field(default="", kw_only=True)

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("Stair.name must not be empty")
        if self.riser_count is not None and self.riser_count <= 0:
            raise ValueError("Stair.riser_count must be > 0")
        for name, value in (("riser_height_m", self.riser_height_m), ("tread_width_m", self.tread_width_m)):
            if value is not None and value <= 0:
                raise ValueError(f"Stair.{name} must be > 0")
        if not self.id:
            object.__setattr__(self, "id", _id("STAIR", self.name))

    @property
    def length_m(self) -> float:
        return self.footprint.length

    @property
    def width_m(self) -> float:
        return self.footprint.width

    @property
    def plan_area_m2(self) -> float:
        return self.footprint.floor_area


@dataclass(frozen=True)
class Terrace:
    """Canonical terrace geometry and construction/material identity."""

    name: str
    footprint: Box3D
    construction_type: str = "concrete"
    material_id: str | None = None
    id: str = field(default="", kw_only=True)

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("Terrace.name must not be empty")
        if not self.construction_type.strip():
            raise ValueError("Terrace.construction_type must not be empty")
        if not self.id:
            object.__setattr__(self, "id", _id("TERRACE", self.name))

    @property
    def length_m(self) -> float:
        return self.footprint.length

    @property
    def width_m(self) -> float:
        return self.footprint.width

    @property
    def plan_area_m2(self) -> float:
        return self.footprint.floor_area
