import pytest
from lat_ces.core.dimensions import Dimension, MASS
from lat_ces.scientific.quantity import PhysicalQuantity
from lat_ces.modules.plenum import FLOW_RATE
from lat_ces.modules.pressure import FanEngine, PRESSURE, POWER


def test_fan_power_calculation():
    engine = FanEngine()

    q = PhysicalQuantity(2.0, FLOW_RATE, 0.05)
    dp = PhysicalQuantity(250.0, PRESSURE, 10.0)

    p_ideal = engine.calculate_fan_power(q, dp, efficiency=1.0)
    assert p_ideal.value == 500.0
    assert p_ideal.dimension == POWER
    assert p_ideal.uncertainty > 0

    p_real = engine.calculate_fan_power(q, dp, efficiency=0.8)
    assert p_real.value == 625.0
    assert p_real.dimension == POWER


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
