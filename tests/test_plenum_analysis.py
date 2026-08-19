import pytest

from lat_ces.scientific.analysis.plenum import PlenumAnalysisEngine, SafetyStatus
from lat_ces.scientific.dimensions.dimension import LENGTH, MASS, TIME
from lat_ces.scientific.equations.engine import DimensionalityError
from lat_ces.scientific.quantities.quantity import PhysicalQuantity
from lat_ces.scientific.units.units import Unit


def test_plenum_analysis_reports_safe_value():
    pascal = Unit("pascal", "Pa", MASS / (LENGTH * TIME**2))
    calculated = PhysicalQuantity(90.0, 2.0, pascal)
    limit = PhysicalQuantity(100.0, 0.0, pascal)

    report = PlenumAnalysisEngine.evaluate_limit(calculated, limit)

    assert report.status is SafetyStatus.SAFE
    assert report.expanded_uncertainty == 4.0
    assert report.margin_to_limit == 10.0


def test_plenum_analysis_reports_metrological_risk_and_critical_excess():
    pascal = Unit("pascal", "Pa", MASS / (LENGTH * TIME**2))

    risk = PlenumAnalysisEngine.evaluate_limit(
        PhysicalQuantity(99.0, 1.0, pascal), PhysicalQuantity(100.0, 0.0, pascal)
    )
    critical = PlenumAnalysisEngine.evaluate_limit(
        PhysicalQuantity(101.0, 1.0, pascal), PhysicalQuantity(100.0, 0.0, pascal)
    )

    assert risk.status is SafetyStatus.METROLOGICAL_RISK
    assert critical.status is SafetyStatus.CRITICAL_EXCEEDED


def test_plenum_analysis_converts_limit_units():
    pascal = Unit("pascal", "Pa", MASS / (LENGTH * TIME**2))
    kilopascal = Unit("kilopascal", "kPa", pascal.dimension, scale_factor=1000.0)

    report = PlenumAnalysisEngine.evaluate_limit(
        PhysicalQuantity(90.0, 2.0, pascal),
        PhysicalQuantity(0.1, 0.0, kilopascal),
    )

    assert report.status is SafetyStatus.SAFE
    assert report.margin_to_limit == 10.0


def test_plenum_analysis_rejects_different_dimensions():
    pascal = Unit("pascal", "Pa", MASS / (LENGTH * TIME**2))
    meter = Unit("meter", "m", LENGTH)

    with pytest.raises(DimensionalityError):
        PlenumAnalysisEngine.evaluate_limit(
            PhysicalQuantity(10.0, 1.0, pascal),
            PhysicalQuantity(10.0, 1.0, meter),
        )