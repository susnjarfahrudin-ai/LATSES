import pytest

from lat_ces.model_elements import bind_product


def test_model_element_resolves_selected_catalog_product():
    element = bind_product("wall-01", "wall", "masonry_block")
    assert element.id == "wall-01"
    assert element.element_type == "wall"
    assert element.product_id == "masonry_block"
    assert element.product().id == "masonry_block"


def test_model_element_rejects_unknown_product():
    with pytest.raises(KeyError):
        bind_product("wall-02", "wall", "does-not-exist")
