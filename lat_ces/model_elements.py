"""Minimal binding between physical model elements and catalog products."""

from dataclasses import dataclass

from .material_interface import get_product


@dataclass(frozen=True)
class ModelElement:
    id: str
    element_type: str
    product_id: str

    def product(self):
        """Resolve this element's catalog product by stable product ID."""
        return get_product(self.product_id)


def bind_product(element_id: str, element_type: str, product_id: str) -> ModelElement:
    """Bind a catalog product to a concrete model element."""
    get_product(product_id)  # fail immediately if the selection is not in the catalog
    return ModelElement(element_id, element_type, product_id)
