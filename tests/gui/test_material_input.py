import pytest

from lat_ces.gui_material_input import material_from_fields


def _valid_fields(**overrides):
    fields = {
        "name": "Porotherm 25",
        "category": "opeka",
        "manufacturer": "Wienerberger",
        "product_id": "P25",
        "density": "850",
        "youngs_modulus": "3000000000",
        "poisson_ratio": "0.2",
        "thermal_conductivity": "0.145",
        "compressive_strength_mpa": "10",
        "dimensions": "0.25,0.20,0.30",
    }
    fields.update(overrides)
    return fields


def test_material_from_fields_builds_canonical_material():
    material = material_from_fields(_valid_fields())
    assert material.name == "Porotherm 25"
    assert material.density == 850.0
    assert material.youngs_modulus == 3_000_000_000.0
    assert material.poisson_ratio == 0.2
    assert material.thermal_conductivity == 0.145
    assert material.compressive_strength_mpa == 10.0
    assert material.dimensions_m == (0.25, 0.20, 0.30)
    assert material.product_id == "P25"
    assert material.manufacturer == "Wienerberger"
    assert material.category == "opeka"


def test_material_from_fields_requires_manufacturer_specification_identity():
    for field in ("category", "manufacturer", "product_id"):
        fields = _valid_fields(**{field: ""})
        with pytest.raises(ValueError, match="Proizvođačka specifikacija"):
            material_from_fields(fields)


def test_material_from_fields_requires_at_least_one_physical_property():
    fields = _valid_fields(
        density="",
        youngs_modulus="",
        thermal_conductivity="",
        compressive_strength_mpa="",
    )
    with pytest.raises(ValueError, match="Najmanje jedno relevantno fizičko svojstvo"):
        material_from_fields(fields)


def test_material_from_fields_rejects_invalid_physical_values():
    for field, value in (
        ("density", "0"),
        ("youngs_modulus", "-1"),
        ("thermal_conductivity", "0"),
        ("compressive_strength_mpa", "-2"),
        ("dimensions", "0.25,-0.10"),
    ):
        fields = _valid_fields(**{field: value})
        with pytest.raises(ValueError):
            material_from_fields(fields)


def test_material_from_fields_requires_name():
    with pytest.raises(ValueError, match="Proizvođačka specifikacija"):
        material_from_fields(_valid_fields(name="   "))
