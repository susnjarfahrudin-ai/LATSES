import pytest

from lat_ces.core.dimensions import DENSITY, DYNAMIC_VISCOSITY, LENGTH, VELOCITY, PRESSURE
from lat_ces.scientific.duct_friction import DuctFrictionModel, DuctError
from lat_ces.scientific.quantity import PhysicalQuantity


def test_friction_loss():
    model = DuctFrictionModel(friction_factor=0.018)
    loss = model.compute_friction_loss(
        length_m=10.0,
        diameter_m=0.5,
        velocity_m_s=5.0,
        air_density=1.2,
    )
    assert loss > 0.0


def test_reynolds_and_friction_factor_are_canonical():
    rho = PhysicalQuantity(1.2, DENSITY, 0.01)
    velocity = PhysicalQuantity(3.0, VELOCITY, 0.1)
    diameter = PhysicalQuantity(0.5, LENGTH, 0.01)
    viscosity = PhysicalQuantity(1.81e-5, DYNAMIC_VISCOSITY, 1e-7)

    reynolds = DuctFrictionModel.calculate_reynolds_number(
        rho, velocity, diameter, viscosity
    )
    friction_factor = DuctFrictionModel.estimate_friction_factor(reynolds)

    assert reynolds > 2300.0
    assert 0.01 < friction_factor < 0.05


def test_reynolds_rejects_wrong_dimension():
    rho = PhysicalQuantity(1.2, DENSITY, 0.01)
    velocity = PhysicalQuantity(3.0, VELOCITY, 0.1)
    diameter = PhysicalQuantity(0.5, LENGTH, 0.01)
    wrong_viscosity = PhysicalQuantity(1.81e-5, DENSITY, 1e-7)

    with pytest.raises(DuctError, match="dynamic_viscosity"):
        DuctFrictionModel.calculate_reynolds_number(
            rho, velocity, diameter, wrong_viscosity
        )


def test_quantity_friction_loss_returns_canonical_pressure():
    model = DuctFrictionModel(friction_factor=0.02)
    length = PhysicalQuantity(10.0, LENGTH, 0.1)
    diameter = PhysicalQuantity(0.5, LENGTH, 0.01)
    density = PhysicalQuantity(1.2, DENSITY, 0.01)
    velocity = PhysicalQuantity(4.0, VELOCITY, 0.1)

    dp = model.compute_quantity_friction_loss(length, diameter, density, velocity)

    assert dp.value == pytest.approx(3.84, abs=1e-2)
    assert dp.dimension is PRESSURE
    assert dp.uncertainty > 0.0
