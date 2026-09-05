"""Canonical sub-zones for MEP systems owned by BuildingModel.mep."""
from __future__ import annotations

from dataclasses import dataclass


ZONE_MODES = ("full", "half_a", "half_b")


@dataclass(frozen=True)
class UnderfloorZone:
    """Spatial coverage of one underfloor system for schematic/engineering routing."""

    id: str
    system_id: str
    room_id: str
    level_id: str
    mode: str = "full"
    split_axis: str = "x"

    def __post_init__(self) -> None:
        if self.mode not in ZONE_MODES:
            raise ValueError(f"unsupported underfloor zone mode: {self.mode}")
        if self.split_axis not in {"x", "y"}:
            raise ValueError("underfloor zone split_axis must be 'x' or 'y'")

    @property
    def zone_count(self) -> int:
        return 1 if self.mode == "full" else 2

    @property
    def zone_index(self) -> int:
        return 0 if self.mode in {"full", "half_a"} else 1

    @property
    def label(self) -> str:
        return {"full": "Cijela prostorija", "half_a": "1/2 — A", "half_b": "1/2 — B"}[self.mode]


__all__ = ["ZONE_MODES", "UnderfloorZone"]
