"""Canonical derived SI units for the Scientific unit system.

This module owns derived-unit definitions.  Primitive unit definitions and
unit algebra remain in :mod:`lat_ces.scientific.units.core`; registry lookup
remains in :mod:`lat_ces.scientific.units.registry`.
"""

from __future__ import annotations

from .core import (
    Unit,
    ampere,
    candela,
    kelvin,
    kilogram,
    meter,
    mole,
    second,
)
from lat_ces.scientific.dimensions.dimension import (
    AMOUNT,
    CURRENT,
    DIMENSIONLESS,
    LENGTH,
    LUMINOUS_INTENSITY,
    MASS,
    TEMPERATURE,
    TIME,
)


kelvin_interval = Unit(
    name="kelvin interval",
    symbol="K",
    dimension=TEMPERATURE,
    scale_factor=1.0,
    offset=0.0,
)


DERIVED_UNITS = {
    DIMENSIONLESS: Unit("dimensionless", "1", DIMENSIONLESS),
    LENGTH: meter,
    MASS: kilogram,
    TIME: second,
    CURRENT: ampere,
    TEMPERATURE: kelvin_interval,
    AMOUNT: mole,
    LUMINOUS_INTENSITY: candela,
    LENGTH / TIME: meter / second,
    LENGTH**2: meter**2,
    LENGTH**3 / TIME: (meter**3) / second,
    MASS / TIME: kilogram / second,
    MASS / (LENGTH**3): kilogram / (meter**3),
    MASS / (LENGTH * (TIME**2)): kilogram / meter / (second**2),
    MASS / (LENGTH * TIME): kilogram / meter / second,
    (MASS * (LENGTH**2)) / (TIME**3): (kilogram * (meter**2)) / (second**3),
    (LENGTH**2) / (TIME**2) / TEMPERATURE: (meter**2) / (second**2) / kelvin_interval,
}


__all__ = ["DERIVED_UNITS", "kelvin_interval"]
