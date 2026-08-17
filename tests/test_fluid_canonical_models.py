from lat_ces.core.dimensions import DENSITY, FLOW_RATE, PRESSURE, POWER, VELOCITY
from lat_ces.scientific.fan_laws import FanAffinityModel
from lat_ces.scientific.fittings import FittingLossModel
from lat_ces.scientific.quantity import PhysicalQuantity
from lat_ces.modules.fan_laws import FanAffinityEngine
from lat_ces.modules.fittings import FittingLossEngine


def _q(value, dimension, uncertainty=0.0):
    return PhysicalQuantity(value=value, dimension=dimension, uncertainty=uncertainty)


def test_fitting_facade_delegates_to_canonical_model():
    density = _q(1.2, DENSITY)
    velocity = _q(5.0, VELOCITY)
    expected = FittingLossModel.compute_pressure_loss(2.0, density, velocity)
    actual = FittingLossEngine.calculate_fitting_loss(2.0, density, velocity)
    assert actual.value == expected.value
    assert actual.dimension is PRESSURE


def test_fan_affinity_facade_delegates_to_canonical_model():
    flow = _q(1.0, FLOW_RATE)
    pressure = _q(100.0, PRESSURE)
    power = _q(200.0, POWER)
    expected = FanAffinityModel.scale_by_rpm(flow, pressure, power, 1000, 1200)
    actual = FanAffinityEngine.scale_by_rpm(flow, pressure, power, 1000, 1200)
    assert [(q.value, q.dimension) for q in actual] == [(q.value, q.dimension) for q in expected]


def test_canonical_models_have_single_public_implementation():
    assert FanAffinityEngine.scale_by_rpm.__func__.__module__ == "lat_ces.modules.fan_laws"
    assert FittingLossEngine.calculate_fitting_loss.__func__.__module__ == "lat_ces.modules.fittings"
