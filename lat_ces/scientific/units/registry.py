"""Canonical SI unit registry used by Scientific Quantity bridges."""

from __future__ import annotations

from lat_ces.scientific.dimensions.dimension import Dimension

from .derived import DERIVED_UNITS, kelvin_interval


def dimension_to_unit(dimension: Dimension):
    """Return the canonical SI unit registered for *dimension*."""
    if dimension in DERIVED_UNITS:
        return DERIVED_UNITS[dimension]
    raise ValueError(f"No canonical SI unit is registered for dimension {dimension!r}")


__all__ = ["DERIVED_UNITS", "dimension_to_unit", "kelvin_interval"]
