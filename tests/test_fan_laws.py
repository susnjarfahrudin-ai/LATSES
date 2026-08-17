from lat_ces.core.dimensions import FLOW_RATE, PRESSURE, POWER
from lat_ces.scientific.quantity import PhysicalQuantity
from lat_ces.modules.fan_laws import FanAffinityEngine


def test_fan_laws_scaling():
    engine = FanAffinityEngine()

    q1 = PhysicalQuantity(2.0, FLOW_RATE, 0.05)
    p1 = PhysicalQuantity(200.0, PRESSURE, 10.0)
    w1 = PhysicalQuantity(500.0, POWER, 25.0)

    q2, p2, w2 = engine.scale_by_rpm(q1, p1, w1, 1000.0, 2000.0)

    assert q2.value == 4.0
    assert p2.value == 800.0
    assert w2.value == 4000.0
