import pytest

from lat_ces.gui_material_input import material_from_fields


def test_material_from_fields_builds_canonical_material():
    material = material_from_fields(
        {
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
    )
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


def test_material_from_fields_allows_blank_optional_properties():
    material = material_from_fields({"name": "Novi materijal"})
    assert material.name == "Novi materijal"
    assert material.density is None
    assert material.thermal_conductivity is None
    assert material.dimensions_m == ()


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("density", "0"),
        ("youngs_modulus", "-1"),
        ("thermal_conductivity", "0"),
        ("compressive_strength_mpa", "-2"),
        ("dimensions", "0.25,-0.10"),
    ],
)
def test_material_from_fields_rejects_invalid_physical_values(field, value):
    fields = {"name": "Test materijal", field: value}
    with pytest.raises(ValueError):
        material_from_fields(fields)


def test_material_from_fields_requires_name():
    with pytest.raises(ValueError, match="Naziv materijala"):
        material_from_fields({"name": "   "})
