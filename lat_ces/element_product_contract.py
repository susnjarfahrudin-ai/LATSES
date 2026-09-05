"""Compatibility contract between model element types and catalog categories."""

from .material_interface import get_product
from .model_elements import ModelElement


ELEMENT_CATEGORIES = {
    "wall": {"construction"},
    "partition": {"construction"},
    "floor_slab": {"construction"},
    "insulation": {"construction"},
    "roof": {"roof"},
    "roof_structure": {"roof_structure"},
    "ventilation": {"ventilation"},
    "air_filter": {"air_quality"},
    "floor_finish": {"finish"},
}


def validate_element_product(element: ModelElement) -> ModelElement:
    """Validate that an element type can use the selected catalog product."""
    allowed = ELEMENT_CATEGORIES.get(element.element_type)
    if allowed is None:
        raise ValueError(f"Unknown model element type: {element.element_type}")

    product = get_product(element.product_id)
    if product is None:
        raise KeyError(f"Unknown catalog product: {element.product_id}")

    if product.category not in allowed:
        raise ValueError(
            f"Product '{element.product_id}' category '{product.category}' "
            f"is incompatible with element type '{element.element_type}'"
        )

    return element


def bind_compatible_product(element_id: str, element_type: str, product_id: str) -> ModelElement:
    """Create and validate a model element/product binding in one operation."""
    element = ModelElement(element_id, element_type, product_id)
    return validate_element_product(element)
