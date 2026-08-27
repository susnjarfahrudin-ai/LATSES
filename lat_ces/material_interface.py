"""Central product catalog used by the LAT-CES GUI and engineering model."""

from .product_schema import Product


MATERIAL_CATALOG = (
    Product("floor_slab", "Međuspratna ploča", "construction"),
    Product("masonry_block", "Nosivi zidni blok", "construction"),
    Product("partition_block", "Pregradni blok", "construction"),
    Product("insulation", "Toplotna izolacija", "construction"),
    Product("floor_finish", "Podna obloga", "finish"),
    Product("roof_cover", "Krovni pokrov", "roof"),
    Product("roof_beam", "Krovna greda", "roof_structure"),
    Product("ventilation_fan", "Ventilator", "ventilation"),
    Product("heat_recovery_unit", "Rekuperator", "ventilation"),
    Product("duct", "Ventilaciona cijev", "ventilation"),
    Product("duct_elbow", "Koljeno", "ventilation"),
    Product("plenum", "Plenum", "ventilation"),
    Product("filter_g4", "G4 filter", "air_quality"),
    Product("filter_f7", "F7 filter", "air_quality"),
)


def material_catalog() -> tuple[Product, ...]:
    """Return the canonical catalog as Product objects."""
    return MATERIAL_CATALOG


def get_product(product_id: str) -> Product | None:
    """Resolve a catalog product by its stable ID."""
    return next((product for product in MATERIAL_CATALOG if product.id == product_id), None)
