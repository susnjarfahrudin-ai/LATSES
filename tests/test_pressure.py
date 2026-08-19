import pytest

from lat_ces.core.dimensions import DENSITY, Dimension, MASS, PRESSURE, VELOCITY, POWER, FLOW_RATE
from lat_ces.scientific.fan_power import FanPowerModel
from lat_ces.scientific.pressure_drop import PressureDropModel
from lat_ces.scientific.quantity import PhysicalQuantity
from lat_ces.modules.pressure import FanEngine


def test_fan_power_calculation():
    engine = FanEngine()

    q = PhysicalQuantity(2.0, FLOW_RATE, 0.05)
    dp = PhysicalQuantity(250.0, PRESSURE, 10.0)

    p_ideal = engine.calculate_fan_power(q, dp, efficiency=1.0)
    assert p_ideal.value == 500.0
    assert p_ideal.dimension is POWER
    assert p_ideal.uncertainty > 0

    p_real = engine.calculate_fan_power(q, dp, efficiency=0.8)
    assert p_real.value == 625.0
    assert p_real.dimension is POWER


def test_fan_power_facade_delegates_to_canonical_model():
    q = PhysicalQuantity(2.0, FLOW_RATE, 0.05)
    dp = PhysicalQuantity(250.0, PRESSURE, 10.0)
    expected = FanPowerModel.calculate(q, dp, efficiency=0.8)
    actual = FanEngine().calculate_fan_power(q, dp, efficiency=0.8)
    assert actual.value == expected.value
    assert actual.uncertainty == expected.uncertainty
    assert actual.dimension is POWER


def test_pressure_drop_quantity_api_uses_canonical_dimensions():
    model = PressureDropModel(loss_coefficient=1.5)
    velocity = PhysicalQuantity(4.0, VELOCITY, 0.1)
    density = PhysicalQuantity(1.2, DENSITY, 0.02)
    dp = model.compute_quantity_pressure_drop(velocity, density)
    assert dp.value == pytest.approx(14.4)
    assert dp.dimension is PRESSURE
    assert dp.uncertainty > 0


def test_pressure_drop_quantity_api_rejects_wrong_dimensions():
    model = PressureDropModel(loss_coefficient=1.5)
    with pytest.raises(ValueError, match="velocity"):
        model.compute_quantity_pressure_drop(PhysicalQuantity(4.0, DENSITY), PhysicalQuantity(1.2, DENSITY))
    with pytest.raises(ValueError, match="density"):
        model.compute_quantity_pressure_drop(PhysicalQuantity(4.0, VELOCITY), PhysicalQuantity(1.2, VELOCITY))


def test_invalid_efficiency():
    engine = FanEngine()
    q = PhysicalQuantity(2.0, FLOW_RATE, 0.05)
    dp = PhysicalQuantity(250.0, PRESSURE, 10.0)

    with pytest.raises(ValueError):
        _ = engine.calculate_fan_power(q, dp, efficiency=0.0)

    with pytest.raises(ValueError):
        _ = engine.calculate_fan_power(q, dp, efficiency=1.2)


def test_invalid_flow_rate_dimension():
    engine = FanEngine()
    wrong_q = PhysicalQuantity(2.0, Dimension(L=1), 0.05)
    dp = PhysicalQuantity(250.0, PRESSURE, 10.0)

    with pytest.raises(ValueError, match="flow_rate"):
        engine.calculate_fan_power(wrong_q, dp)


def test_invalid_pressure_drop_dimension():
    engine = FanEngine()
    q = PhysicalQuantity(2.0, FLOW_RATE, 0.05)
    wrong_dp = PhysicalQuantity(250.0, MASS, 10.0)

    with pytest.raises(ValueError, match="pressure_drop"):
        engine.calculate_fan_power(q, wrong_dp)
