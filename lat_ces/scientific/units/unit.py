"""Compatibility facade for the canonical LAT-CES Unit engine."""

from lat_ces.core.dimensions import (
    ACCELERATION,
    AMOUNT,
    CURRENT,
    DENSITY,
    FORCE,
    LENGTH,
    LUMINOUS_INTENSITY,
    MASS,
    TEMPERATURE,
    TIME,
    VELOCITY,
    Dimension,
    Unit,
    UnitSKOError,
)


UnitError = UnitSKOError

METER = Unit("meter", "m", LENGTH, 1.0)
KILOGRAM = Unit("kilogram", "kg", MASS, 1.0)
SECOND = Unit("second", "s", TIME, 1.0)
AMPERE = Unit("ampere", "A", CURRENT, 1.0)
KELVIN = Unit("kelvin", "K", TEMPERATURE, 1.0)
MOLE = Unit("mole", "mol", AMOUNT, 1.0)
CANDELA = Unit("candela", "cd", LUMINOUS_INTENSITY, 1.0)
NEWTON = Unit("newton", "N", FORCE, 1.0)
METER_PER_SECOND = METER / SECOND

SI_REGISTRY = {
    "m": METER,
    "kg": KILOGRAM,
    "s": SECOND,
    "A": AMPERE,
    "K": KELVIN,
    "mol": MOLE,
    "cd": CANDELA,
    "N": NEWTON,
    "m/s": METER_PER_SECOND,
}

__all__ = [
    "Unit",
    "UnitError",
    "SI_REGISTRY",
    "Dimension",
    "ACCELERATION",
    "AMOUNT",
    "CURRENT",
    "DENSITY",
    "FORCE",
    "LENGTH",
    "LUMINOUS_INTENSITY",
    "MASS",
    "TEMPERATURE",
    "TIME",
    "VELOCITY",
]
