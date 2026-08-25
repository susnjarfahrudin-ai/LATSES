"""
LAT-CES Scientific Core Registry Tests
"""

import pytest

from lat_ces.scientific.registry.constants import (
    GRAVITATIONAL_CONSTANT,
    PLANCK_CONSTANT,
    SPEED_OF_LIGHT,
)
from lat_ces.scientific.registry.registry import RegistryError, ScientificKnowledgeRegistry
from lat_ces.scientific.units.dimension import LENGTH
from lat_ces.scientific.units.unit import METER


def test_registry_unit_registration_and_lookup():
    reg = ScientificKnowledgeRegistry()
    reg.register_unit("m", METER)
    assert reg.get_unit("m") == METER


def test_registry_duplicate_registration_fails():
    reg = ScientificKnowledgeRegistry()
    reg.register_unit("m", METER)
    with pytest.raises(RegistryError):
        reg.register_unit("m", METER)


def test_registry_lookup_nonexistent():
    reg = ScientificKnowledgeRegistry()
    with pytest.raises(RegistryError):
        reg.get_unit("non_existent_unit")


def test_registry_physical_constants_are_typed_and_retrievable():
    reg = ScientificKnowledgeRegistry()
    reg.register_constant("c", SPEED_OF_LIGHT)
    reg.register_constant("h", PLANCK_CONSTANT)
    reg.register_constant("G", GRAVITATIONAL_CONSTANT)

    assert reg.get_constant("c") is SPEED_OF_LIGHT
    assert reg.get_constant("h").value == pytest.approx(6.62607015e-34)
    assert reg.get_constant("G").value == pytest.approx(6.67430e-11)
    assert reg.get_constant("c").unit.dimension == LENGTH / lat_ces.scientific.units.dimension.TIME


def test_registry_duplicate_constant_registration_fails():
    reg = ScientificKnowledgeRegistry()
    reg.register_constant("c", SPEED_OF_LIGHT)
    with pytest.raises(RegistryError):
        reg.register_constant("c", SPEED_OF_LIGHT)


def test_registry_rejects_untyped_constant():
    reg = ScientificKnowledgeRegistry()
    with pytest.raises(RegistryError):
        reg.register_constant("bad", object())
