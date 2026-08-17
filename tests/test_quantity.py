import pytest
import math
from lat_ces.core.dimensions import LENGTH, TIME, VELOCITY
from lat_ces.scientific.quantity import PhysicalQuantity

def test_quantity_creation():
    d = PhysicalQuantity(value=10.0, dimension=LENGTH, uncertainty=0.1)
    assert d.value == 10.0
    assert d.dimension == LENGTH
    assert d.uncertainty == 0.1

def test_quantity_addition_success():
    d1 = PhysicalQuantity(10.0, LENGTH, 0.3)
    d2 = PhysicalQuantity(5.0, LENGTH, 0.4)
    res = d1 + d2
    assert res.value == 15.0
    assert res.dimension == LENGTH
    assert math.isclose(res.uncertainty, 0.5)

def test_quantity_addition_dimension_mismatch():
    d = PhysicalQuantity(10.0, LENGTH, 0.1)
    t = PhysicalQuantity(2.0, TIME, 0.05)
    with pytest.raises(ValueError):
        _ = d + t

def test_quantity_division_velocity():
    d = PhysicalQuantity(100.0, LENGTH, 2.0)
    t = PhysicalQuantity(10.0, TIME, 0.1)
    v = d / t
    assert v.value == 10.0
    assert v.dimension == VELOCITY
    expected_u = 10.0 * math.sqrt((2.0/100.0)**2 + (0.1/10.0)**2)
    assert math.isclose(v.uncertainty, expected_u)
