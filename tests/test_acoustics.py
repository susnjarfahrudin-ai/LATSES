import math
import pytest
from lat_ces.core.dimensions import Dimension, PRESSURE
from lat_ces.scientific.quantity.quantity import PhysicalQuantity
from lat_ces.modules.acoustics import AcousticsEngine, P_REF


def test_pressure_to_db():
    assert math.isclose(AcousticsEngine.pressure_to_db(P_REF), 0.0, abs_tol=1e-5)

    db_1pa = AcousticsEngine.pressure_to_db(1.0)
    assert math.isclose(db_1pa, 93.979, abs_tol=1e-3)


def test_pressure_quantity_to_db():
    pressure = PhysicalQuantity(P_REF, PRESSURE, 0.0)
    assert math.isclose(AcousticsEngine.pressure_to_db(pressure), 0.0, abs_tol=1e-5)


def test_pressure_quantity_dimension_validation():
    wrong_dimension = PhysicalQuantity(1.0, Dimension(L=1), 0.0)
    with pytest.raises(ValueError):
        AcousticsEngine.pressure_to_db(wrong_dimension)


def test_combine_noise_levels():
    combined = AcousticsEngine.combine_noise_levels([50.0, 50.0])
    assert math.isclose(combined, 53.01, abs_tol=0.01)


def test_noise_acceptability():
    assert AcousticsEngine.is_noise_acceptable(40.0, max_limit_db=45.0) is True
    assert AcousticsEngine.is_noise_acceptable(50.0, max_limit_db=45.0) is False
