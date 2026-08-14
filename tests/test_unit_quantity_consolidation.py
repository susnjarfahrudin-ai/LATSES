from lat_ces.core.dimensions import LENGTH, TIME, Unit
from lat_ces.modules.quantity import PhysicalQuantity as LegacyPhysicalQuantity
from lat_ces.scientific.quantities.quantity import PhysicalQuantity
from lat_ces.scientific.units.quantity import Quantity
from lat_ces.scientific.units.unit import Unit as FacadeUnit


def test_unit_facade_is_canonical_unit():
    assert FacadeUnit is Unit


def test_legacy_physical_quantity_uses_canonical_engine():
    legacy = LegacyPhysicalQuantity(2.0, LENGTH, 0.1)
    assert isinstance(legacy, PhysicalQuantity)
    assert legacy.dimension == LENGTH
    assert legacy.unit.dimension == LENGTH


def test_quantity_facade_uses_canonical_physical_quantity():
    meter = Unit("meter", "m", LENGTH)
    quantity = Quantity(2.0, meter, 0.1)
    assert isinstance(quantity, PhysicalQuantity)
    assert quantity.dimension == LENGTH


def test_canonical_arithmetic_remains_dimensionally_traced():
    meter = Unit("meter", "m", LENGTH)
    second = Unit("second", "s", TIME)
    distance = PhysicalQuantity(10.0, 0.1, meter)
    duration = PhysicalQuantity(2.0, 0.01, second)

    velocity = distance / duration

    assert velocity.dimension == LENGTH / TIME
    assert velocity.unit.dimension == LENGTH / TIME
