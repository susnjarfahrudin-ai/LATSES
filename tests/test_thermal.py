import pytest
from lat_ces.core.dimensions import Dimension, MASS
from lat_ces.scientific.quantity import PhysicalQuantity
from lat_ces.modules.plenum import MASS_FLOW
from lat_ces.modules.thermal import ThermalEngine, TEMPERATURE, SPECIFIC_HEAT, HEAT_RATE


def test_heat_rate_calculation():
    engine = ThermalEngine()

    mass_flow = PhysicalQuantity(2.0, MASS_FLOW, 0.05)
    cp = PhysicalQuantity(1005.0, SPECIFIC_HEAT, 5.0)
    delta_T = PhysicalQuantity(10.0, TEMPERATURE, 0.2)

    q_dot = engine.calculate_heat_rate(mass_flow, cp, delta_T)

    assert q_dot.value == 20100.0
    assert q_dot.dimension == HEAT_RATE
    assert q_dot.uncertainty > 0


def test_invalid_dimension_thermal():
    engine = ThermalEngine()

    mass_flow = PhysicalQuantity(2.0, MASS_FLOW, 0.05)
    cp = PhysicalQuantity(1005.0, SPECIFIC_HEAT, 5.0)
    wrong_dim = PhysicalQuantity(10.0, MASS, 0.2)

    with pytest.raises(ValueError):
        _ = engine.calculate_heat_rate(mass_flow, cp, wrong_dim)


def test_invalid_mass_flow_dimension_thermal():
    engine = ThermalEngine()
    wrong_mass_flow = PhysicalQuantity(2.0, MASS, 0.05)
    cp = PhysicalQuantity(1005.0, SPECIFIC_HEAT, 5.0)
    delta_T = PhysicalQuantity(10.0, TEMPERATURE, 0.2)

    with pytest.raises(ValueError, match="mass_flow"):
        engine.calculate_heat_rate(wrong_mass_flow, cp, delta_T)


def test_invalid_specific_heat_dimension_thermal():
    engine = ThermalEngine()
    mass_flow = PhysicalQuantity(2.0, MASS_FLOW, 0.05)
    wrong_cp = PhysicalQuantity(1005.0, MASS, 5.0)
    delta_T = PhysicalQuantity(10.0, TEMPERATURE, 0.2)

    with pytest.raises(ValueError, match="specific_heat"):
        engine.calculate_heat_rate(mass_flow, wrong_cp, delta_T)
