import pytest

from lat_ces.scientific.dimensions.dimension import DIMENSIONLESS, LENGTH, MASS, TEMPERATURE, TIME
from lat_ces.scientific.equations.engine import PhysicalDomainError
from lat_ces.scientific.equations.dimensionless import (
    BiotNumberEquation,
    FourierNumberEquation,
    MachNumberEquation,
    NusseltNumberEquation,
    PrandtlNumberEquation,
    ReynoldsNumberEquation,
)
from lat_ces.scientific.quantity import PhysicalQuantity
from lat_ces.scientific.units.units import Unit


DIMENSIONLESS_UNIT = Unit("dimensionless", "-", DIMENSIONLESS)
RHO = Unit("kilogram per cubic meter", "kg/m3", MASS / (LENGTH**3))
M_S = Unit("meter per second", "m/s", LENGTH / TIME)
M = Unit("meter", "m", LENGTH)
MU = Unit("pascal second", "Pa s", MASS / (LENGTH * TIME))
S = Unit("second", "s", TIME)
M2_S = Unit("square meter per second", "m2/s", LENGTH**2 / TIME)
H = Unit("watt per square meter kelvin", "W/(m2 K)", MASS / (TIME**3 * TEMPERATURE))
K = Unit("watt per meter kelvin", "W/(m K)", MASS * LENGTH / (TIME**3 * TEMPERATURE))


def test_reynolds_number():
    result = ReynoldsNumberEquation().calculate(
        density=PhysicalQuantity(1.2, 0.0, RHO),
        velocity=PhysicalQuantity(5.0, 0.0, M_S),
        characteristic_length=PhysicalQuantity(0.1, 0.0, M),
        dynamic_viscosity=PhysicalQuantity(1.8e-5, 0.0, MU),
    )
    assert result.value == pytest.approx(33333.3333333333)
    assert result.unit.dimension == DIMENSIONLESS


def test_mach_number():
    result = MachNumberEquation().calculate(
        velocity=PhysicalQuantity(68.6, 0.0, M_S),
        speed_of_sound=PhysicalQuantity(343.0, 0.0, M_S),
    )
    assert result.value == pytest.approx(0.2)
    assert result.unit.symbol == "-"


def test_prandtl_number():
    result = PrandtlNumberEquation().calculate(
        kinematic_viscosity=PhysicalQuantity(1.5e-5, 0.0, M2_S),
        thermal_diffusivity=PhysicalQuantity(2.14e-5, 0.0, M2_S),
    )
    assert result.value == pytest.approx(0.7009345794)


def test_nusselt_number():
    result = NusseltNumberEquation().calculate(
        heat_transfer_coefficient=PhysicalQuantity(10.0, 0.0, H),
        characteristic_length=PhysicalQuantity(0.5, 0.0, M),
        thermal_conductivity=PhysicalQuantity(0.5, 0.0, K),
    )
    assert result.value == pytest.approx(10.0)


def test_biot_number():
    result = BiotNumberEquation().calculate(
        heat_transfer_coefficient=PhysicalQuantity(10.0, 0.0, H),
        characteristic_length=PhysicalQuantity(0.05, 0.0, M),
        thermal_conductivity=PhysicalQuantity(0.5, 0.0, K),
    )
    assert result.value == pytest.approx(1.0)


def test_fourier_number():
    result = FourierNumberEquation().calculate(
        thermal_diffusivity=PhysicalQuantity(1.0e-5, 0.0, M2_S),
        time=PhysicalQuantity(100.0, 0.0, S),
        characteristic_length=PhysicalQuantity(0.1, 0.0, M),
    )
    assert result.value == pytest.approx(0.1)


def test_reynolds_rejects_zero_viscosity():
    with pytest.raises(PhysicalDomainError):
        ReynoldsNumberEquation().calculate(
            density=PhysicalQuantity(1.2, 0.0, RHO),
            velocity=PhysicalQuantity(5.0, 0.0, M_S),
            characteristic_length=PhysicalQuantity(0.1, 0.0, M),
            dynamic_viscosity=PhysicalQuantity(0.0, 0.0, MU),
        )


def test_fourier_rejects_zero_length():
    with pytest.raises(PhysicalDomainError):
        FourierNumberEquation().calculate(
            thermal_diffusivity=PhysicalQuantity(1.0e-5, 0.0, M2_S),
            time=PhysicalQuantity(100.0, 0.0, S),
            characteristic_length=PhysicalQuantity(0.0, 0.0, M),
        )
