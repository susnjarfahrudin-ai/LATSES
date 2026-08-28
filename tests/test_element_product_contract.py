import pytest

from lat_ces.element_product_contract import bind_compatible_product


def test_compatible_wall_product_is_accepted():
    element = bind_compatible_product("wall-01", "wall", "masonry_block")
    assert element.product().id == "masonry_block"


def test_compatible_air_filter_product_is_accepted():
    element = bind_compatible_product("filter-01", "air_filter", "filter_f7")
    assert element.product().id == "filter_f7"


def test_f7_filter_cannot_be_used_as_wall():
    with pytest.raises(ValueError, match="incompatible"):
        bind_compatible_product("wall-02", "wall", "filter_f7")


def test_unknown_element_type_is_rejected():
    with pytest.raises(ValueError, match="Unknown model element type"):
        bind_compatible_product("x-01", "unknown", "masonry_block")
