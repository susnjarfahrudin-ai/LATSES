"""Deterministic schematic routing for canonical underfloor heating circuits.

The router uses only canonical room geometry and requested pipe spacing. It does
not claim thermal output, hydraulic adequacy, bend-radius compliance or final
installation design.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import hypot


@dataclass(frozen=True)
class UnderfloorRoute:
    points_m: tuple[tuple[float, float, float], ...]
    length_m: float
    spacing_m: float
    clearance_m: float
    status: str = "SCHEMATIC"


def route_room_serpentine(room, spacing_m: float, clearance_m: float | None = None) -> UnderfloorRoute:
    """Create a deterministic serpentine polyline inside a rectangular room."""
    if spacing_m <= 0:
        raise ValueError("spacing_m must be > 0")
    footprint = room.footprint
    length = float(footprint.length)
    width = float(footprint.width)
    if length <= 0 or width <= 0:
        raise ValueError("room footprint must have positive dimensions")

    clearance = float(clearance_m) if clearance_m is not None else min(0.10, spacing_m / 2.0)
    if clearance < 0:
        raise ValueError("clearance_m must be >= 0")
    if 2.0 * clearance >= length or 2.0 * clearance >= width:
        raise ValueError("clearance leaves no routable room area")

    x0 = float(footprint.origin.x) + clearance
    y0 = float(footprint.origin.y) + clearance
    x1 = float(footprint.origin.x) + length - clearance
    y1 = float(footprint.origin.y) + width - clearance

    span = y1 - y0
    passes = max(1, int(span / spacing_m) + 1)
    if passes == 1:
        y_levels = [y0]
    else:
        step = span / (passes - 1)
        y_levels = [y0 + i * step for i in range(passes)]

    points: list[tuple[float, float, float]] = []
    for index, y in enumerate(y_levels):
        if index % 2 == 0:
            points.append((x0, y, 0.0))
            points.append((x1, y, 0.0))
        else:
            points.append((x1, y, 0.0))
            points.append((x0, y, 0.0))

    total = 0.0
    for a, b in zip(points, points[1:]):
        total += hypot(b[0] - a[0], b[1] - a[1])

    return UnderfloorRoute(
        points_m=tuple(points),
        length_m=total,
        spacing_m=spacing_m,
        clearance_m=clearance,
    )


__all__ = ["UnderfloorRoute", "route_room_serpentine"]
