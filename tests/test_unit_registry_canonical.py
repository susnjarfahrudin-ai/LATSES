from lat_ces.scientific.dimensions.dimension import LENGTH, PRESSURE
from lat_ces.scientific.units.core import meter
from lat_ces.scientific.units.derived import DERIVED_UNITS
from lat_ces.scientific.units.registry import dimension_to_unit


def test_registry_uses_canonical_derived_unit_table():
    assert dimension_to_unit(LENGTH) is meter
    assert dimension_to_unit(PRESSURE) is DERIVED_UNITS[PRESSURE]


def test_registry_exposes_single_derived_unit_table():
    assert dimension_to_unit(PRESSURE) is DERIVED_UNITS[PRESSURE]
