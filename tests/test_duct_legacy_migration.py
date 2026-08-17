import math

from lat_ces.core.dimensions import DENSITY, VELOCITY, LENGTH, PRESSURE
from lat_ces.modules.duct import DuctFrictionEngine, DuctFrictionModel
from lat_ces.scientific.quantity.quantity import PhysicalQuantity


def test_legacy_duct_facade_uses_canonical_model():
    assert DuctFrictionModel.__module__ == "lat_ces.scientific.duct_friction"


def test_legacy_duct_facade_preserves_friction_loss_contract():
    engine = DuctFrictionEngine()
    length = PhysicalQuantity(10.0, LENGTH, 0.1)
    diameter = PhysicalQuantity(0.5, LENGTH, 0.01)
    density = PhysicalQuantity(1.2, DENSITY, 0.01)
    velocity = PhysicalQuantity(4.0, VELOCITY, 0.1)

    result = engine.calculate_friction_loss(0.02, length, diameter, density, velocity)

    assert math.isclose(result.value, 3.84, abs_tol=1e-2)
    assert result.dimension == PRESSURE
    assert result.uncertainty > 0
