import math
import pytest
from lat_ces.core.dimensions import (
    Dimension,
    AREA as CORE_AREA,
    FLOW_RATE as CORE_FLOW_RATE,
    DENSITY as CORE_DENSITY,
    MASS_FLOW as CORE_MASS_FLOW,
)
from lat_ces.scientific.quantity import PhysicalQuantity
from lat_ces.modules.plenum import PlenumEngine, AREA, FLOW_RATE, DENSITY, MASS_FLOW


def test_plenum_dimensions_are_canonical_core_objects():
    assert AREA is CORE_AREA
    assert FLOW_RATE is CORE_FLOW_RATE
    assert DENSITY is CORE_DENSITY
    assert MASS_FLOW is CORE_MASS_FLOW


def test_plenum_rejects_wrong_airflow_dimensions():
    engine = PlenumEngine()
    area = PhysicalQuantity(2.0, AREA, 0.05)
    wrong_velocity = PhysicalQuantity(3.0, Dimension(L=1), 0.1)

    with pytest.raises(ValueError, match="velocity"):
        engine.calculate_airflow(area, wrong_velocity)


def test_plenum_rejects_wrong_mass_flow_input_dimensions():
    engine = PlenumEngine()
    wrong_density = PhysicalQuantity(1.2, CORE_FLOW_RATE, 0.01)
    flow_rate = PhysicalQuantity(5.0, FLOW_RATE, 0.1)

    with pytest.raises(ValueError, match="density"):
        engine.calculate_mass_flow(wrong_density, flow_rate)


def test_plenum_flow_calculation():
    engine = PlenumEngine()

    area = PhysicalQuantity(2.0, AREA, 0.05)
    velocity = PhysicalQuantity(3.0, Dimension(L=1, T=-1), 0.1)

    q = engine.calculate_airflow(area, velocity)

    assert q.value == 6.0
    assert q.dimension == FLOW_RATE
    assert q.uncertainty > 0


def test_plenum_mass_flow_calculation():
    engine = PlenumEngine()

    density = PhysicalQuantity(1.2, DENSITY, 0.01)
    q = PhysicalQuantity(5.0, FLOW_RATE, 0.1)

    m_dot = engine.calculate_mass_flow(density, q)

    assert m_dot.value == 6.0
    assert m_dot.dimension == MASS_FLOW
