import math

from lat_ces.core.dimensions import LENGTH, MASS, TIME, VELOCITY
from lat_ces.core.dimensions import Unit
from lat_ces.scientific.quantity import PhysicalQuantity
from lat_ces.scientific.units.registry import dimension_to_unit, kelvin_interval


def test_canonical_quantity_is_authoritative():
    quantity = PhysicalQuantity(10.0, LENGTH, 0.1)
    assert quantity.__class__ is PhysicalQuantity
    assert quantity.dimension == LENGTH
    assert quantity.unit is dimension_to_unit(LENGTH)
    assert isinstance(quantity.unit, Unit)


def test_dimension_mapping_uses_canonical_units():
    quantity = PhysicalQuantity(10.0, LENGTH, 0.1)
    assert quantity.dimension == LENGTH
    assert quantity.unit is dimension_to_unit(LENGTH)


def test_dimension_keyword_form_is_preserved():
    quantity = PhysicalQuantity(value=10.0, dimension=LENGTH, uncertainty=0.1)
    assert quantity.value == 10.0
    assert quantity.dimension == LENGTH
    assert quantity.uncertainty == 0.1


def test_derived_dimension_mapping_is_canonical():
    quantity = PhysicalQuantity(100.0, LENGTH, 2.0) / PhysicalQuantity(10.0, TIME, 0.1)
    assert quantity.dimension == VELOCITY
    assert quantity.unit == dimension_to_unit(VELOCITY)
    expected_u = 10.0 * math.sqrt((2.0 / 100.0) ** 2 + (0.1 / 10.0) ** 2)
    assert math.isclose(quantity.uncertainty, expected_u)


def test_temperature_interval_is_zero_offset():
    assert kelvin_interval.dimension.Theta == 1
    assert kelvin_interval.offset == 0.0
    assert kelvin_interval.scale_factor == 1.0
