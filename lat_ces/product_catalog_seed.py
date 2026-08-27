"""Curated real-product seed data for LAT-CES integration tests.

Values are copied only where available from the cited manufacturer pages.
Missing engineering properties intentionally remain unset rather than guessed.
"""

from lat_ces.product_schema import Product


PRODUCT_CATALOG_SEED = (
    Product(
        id="wienerberger-porotherm-25-s",
        name="Porotherm 25 S",
        category="masonry_block",
        material="hollow clay block",
        dimensions="375 x 250 x 238 mm",
        mass_kg_per_unit=15.10,
        density_kg_m3=630.0,
        thermal_conductivity_w_mk=0.145,
        manufacturer="Wienerberger",
        source="https://www.wienerberger.ba/proizvodi/zid/porotherm-opeka/porotherm-25-s.html",
    ),
    Product(
        id="knauf-drystar-12-5",
        name="Drystar ploča 12,5 mm",
        category="partition_board",
        material="gypsum board",
        dimensions="1250 x 2000 x 12.5 mm",
        mass_kg_per_unit=27.9,
        manufacturer="Knauf",
        source="https://knauf.com/hr-BA/p/proizvod/drystar-ploca-12-5mm-12560_0259",
    ),
    Product(
        id="knauf-sonicboard-12-5",
        name="Sonicboard ploča tip D 12,5 mm",
        category="acoustic_partition_board",
        material="high-density gypsum board",
        dimensions="1250 x 2000 x 12.5 mm",
        mass_kg_per_unit=25.5,
        manufacturer="Knauf",
        source="https://knauf.com/sr-RS/p/proizvod/sonicboard-ploca-tip-d-12-5-mm-14767_0378",
    ),
    Product(
        id="knauf-omnifit-slab-32-100",
        name="OmniFit Slab 32, 100 mm",
        category="insulation",
        material="glass mineral wool",
        dimensions="600 x 1200 x 100 mm",
        thermal_conductivity_w_mk=0.032,
        manufacturer="Knauf Insulation",
        source="https://knauf.com/en-GB/p/product/omnifit-r-slab-32-27984_4206",
    ),
    Product(
        id="tondach-planoton-30",
        name="Tondach Planoton 30",
        category="roof_cover",
        material="clay roof tile",
        dimensions="190 x 400 mm",
        mass_kg_per_unit=2.0,
        manufacturer="Wienerberger / Tondach",
        source="https://www.wienerberger.ba/proizvodi/krov/tondach-crijep/planoton-30-natur-color-crna.html",
    ),
    Product(
        id="zehnder-comfoair-q350-tr",
        name="ComfoAir Q350 TR",
        category="heat_recovery_ventilation",
        manufacturer="Zehnder",
        source="https://www.international.zehnder-systems.com/en/comfortable-indoor-ventilation/products/units/ventilation-units-up-to-600-m3/h/zehnder-comfoair-q350-tr",
    ),
)


def seed_products() -> tuple[Product, ...]:
    return PRODUCT_CATALOG_SEED
