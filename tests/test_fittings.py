import math
import pytest
from lat_ces.core.dimensions import DENSITY, VELOCITY, LENGTH, PRESSURE
from lat_ces.scientific.quantity import PhysicalQuantity
from lat_ces.modules.fittings import FittingLossEngine


def test_fitting_loss():
    engine = FittingLossEngine()

    zeta = 0.5
    rho = PhysicalQuantity(1.2, DENSITY, 0.01)
    v = PhysicalQuantity(4.0, VELOCITY, 0.1)

    dp = engine.calculate_fitting_loss(zeta, rho, v)

    assert math.isclose(dp.value, 4.8, abs_tol=1e-2)
    assert dp.dimension == PRESSURE
    assert dp.uncertainty > 0


def test_fitting_loss_rejects_wrong_density_dimension():
    engine = FittingLossEngine()
    wrong_rho = PhysicalQuantity(1.2, LENGTH, 0.01)
    v = PhysicalQuantity(4.0, VELOCITY, 0.1)

    with pytest.raises(ValueError, match="density"):
        engine.calculate_fitting_loss(0.5, wrong_rho, v)


def test_fitting_loss_rejects_wrong_velocity_dimension():
    engine = FittingLossEngine()
    rho = PhysicalQuantity(1.2, DENSITY, 0.01)
    wrong_v = PhysicalQuantity(4.0, LENGTH, 0.1)

    with pytest.raises(ValueError, match="velocity"):
        engine.calculate_fitting_loss(0.5, rho, wrong_v)
