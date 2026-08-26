import pytest

from lat_ces.scientific.quantity import Quantity, QuantityError
from lat_ces.scientific.units.core import centimeter, kilogram, meter, second


def test_quantity_converts_and_adds_compatible_units():
    length = Quantity(1.0, meter)
    two_centimeters = Quantity(2.0, centimeter)

    result = length + two_centimeters

    assert result.unit == meter
    assert result.value == pytest.approx(1.02)


def test_quantity_rejects_dimension_mismatch():
    with pytest.raises(QuantityError):
        _ = Quantity(1.0, meter) + Quantity(1.0, kilogram)


def test_quantity_multiplication_builds_composite_dimension():
    result = Quantity(5.0, meter) * Quantity(2.0, second)

    assert result.value == pytest.approx(10.0)
    assert result.dimension == meter.dimension * second.dimension


def test_quantity_division_builds_composite_dimension():
    result = Quantity(10.0, meter) / Quantity(2.0, second)

    assert result.value == pytest.approx(5.0)
    assert result.dimension == meter.dimension / second.dimension


def test_quantity_preserves_provenance_and_uncertainty_reference():
    result = Quantity(21.0, meter, provenance="model-room-01", uncertainty_ref="U-01")

    assert result.provenance == "model-room-01"
    assert result.uncertainty_ref == "U-01"


def test_quantity_rejects_zero_divisor():
    with pytest.raises(ZeroDivisionError):
        _ = Quantity(1.0, meter) / Quantity(0.0, second)
