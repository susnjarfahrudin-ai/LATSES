import math
import pytest
from lat_ces.core.dimensions import DENSITY, VELOCITY, LENGTH, DYNAMIC_VISCOSITY, Dimension
from lat_ces.modules.quantity import PhysicalQuantity
from lat_ces.modules.pressure import PRESSURE
from lat_ces.modules.duct import DuctFrictionEngine, VISCOSITY_AIR


def test_duct_viscosity_dimension_is_canonical():
    assert VISCOSITY_AIR is DYNAMIC_VISCOSITY


def test_reynolds_and_friction_factor():
    engine = DuctFrictionEngine()

    rho = PhysicalQuantity(1.2, DENSITY, 0.01)
    v = PhysicalQuantity(3.0, VELOCITY, 0.1)
    d_h = PhysicalQuantity(0.5, LENGTH, 0.01)
    mu = PhysicalQuantity(1.81e-5, VISCOSITY_AIR, 1e-7)

    re = engine.calculate_reynolds_number(rho, v, d_h, mu)
    assert re > 2300.0

    f = engine.estimate_friction_factor(re)
    assert 0.01 < f < 0.05


def test_reynolds_rejects_wrong_dynamic_viscosity_dimension():
    engine = DuctFrictionEngine()
    rho = PhysicalQuantity(1.2, DENSITY, 0.01)
    v = PhysicalQuantity(3.0, VELOCITY, 0.1)
    d_h = PhysicalQuantity(0.5, LENGTH, 0.01)
    wrong_mu = PhysicalQuantity(1.81e-5, DENSITY, 1e-7)

    with pytest.raises(ValueError, match="dynamic_viscosity"):
        engine.calculate_reynolds_number(rho, v, d_h, wrong_mu)


def test_friction_loss_calculation():
    engine = DuctFrictionEngine()

    f = 0.02
    length = PhysicalQuantity(10.0, LENGTH, 0.1)
    d_h = PhysicalQuantity(0.5, LENGTH, 0.01)
    rho = PhysicalQuantity(1.2, DENSITY, 0.01)
    v = PhysicalQuantity(4.0, VELOCITY, 0.1)

    dp = engine.calculate_friction_loss(f, length, d_h, rho, v)

    assert math.isclose(dp.value, 3.84, abs_tol=1e-2)
    assert dp.dimension == PRESSURE
    assert dp.uncertainty > 0


def test_friction_loss_rejects_wrong_density_dimension():
    engine = DuctFrictionEngine()

    f = 0.02
    length = PhysicalQuantity(10.0, LENGTH, 0.1)
    d_h = PhysicalQuantity(0.5, LENGTH, 0.01)
    wrong_rho = PhysicalQuantity(1.2, VELOCITY, 0.01)
    v = PhysicalQuantity(4.0, VELOCITY, 0.1)

    with pytest.raises(ValueError, match="density"):
        engine.calculate_friction_loss(f, length, d_h, wrong_rho, v)
