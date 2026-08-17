from lat_ces.core.dimensions import (
    AMOUNT,
    CURRENT,
    FORCE,
    LENGTH,
    LUMINOUS_INTENSITY,
    MASS,
    TEMPERATURE,
    TIME,
    VELOCITY,
    Dimension,
    ampere,
    candela,
    centimeter,
    celsius,
    convert_unit,
    kelvin,
    kilogram,
    meter,
    mole,
    second,
)
from lat_ces.scientific.dimensions.dimension import Dimension as CanonicalDimension


def test_dimension_algebra():
    calculated_velocity = LENGTH / TIME
    assert calculated_velocity == VELOCITY

    mass_dim = Dimension(M=1)
    acc_dim = Dimension(L=1, T=-2)
    calculated_force = mass_dim * acc_dim
    assert calculated_force == FORCE

    assert MASS == Dimension(M=1)


def test_dimension_facade_is_canonical():
    assert Dimension is CanonicalDimension


def test_si_base_units_registered():
    assert meter.symbol == "m" and meter.dimension == LENGTH
    assert kilogram.symbol == "kg" and kilogram.dimension == MASS
    assert second.symbol == "s" and second.dimension == TIME
    assert ampere.symbol == "A" and ampere.dimension == CURRENT
    assert kelvin.symbol == "K" and kelvin.dimension == TEMPERATURE
    assert mole.symbol == "mol" and mole.dimension == AMOUNT
    assert candela.symbol == "cd" and candela.dimension == LUMINOUS_INTENSITY


def test_derived_unit_dimension():
    newton = kilogram * meter / (second * second)
    assert newton.dimension == FORCE


def test_linear_unit_conversion():
    assert convert_unit(1.0, meter, centimeter) == 100.0


def test_temperature_offset_conversion():
    assert convert_unit(0.0, celsius, kelvin) == 273.15


def test_unit_is_sko_compliant():
    assert meter.uuid is not None
    assert meter.status in ["DRAFT", "REVIEWED", "VERIFIED", "VALIDATED", "RELEASED"]
