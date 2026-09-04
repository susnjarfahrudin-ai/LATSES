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
        product = get_product(self.product_id)
        if product is None:
            raise KeyError(f"Unknown catalog product: {self.product_id}")
        return product


def bind_product(element_id: str, element_type: str, product_id: str) -> ModelElement:
    """Bind a catalog product to a concrete model element."""
    product = get_product(product_id)
    if product is None:
        raise KeyError(f"Unknown catalog product: {product_id}")
    return ModelElement(element_id, element_type, product_id)
