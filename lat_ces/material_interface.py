"""Minimal central product/material catalog contract for LAT-CES GUI."""

MATERIAL_CATALOG = (
    ("floor_slab", "Međuspratna ploča", "construction"),
    ("masonry_block", "Nosivi zidni blok", "construction"),
    ("partition_block", "Pregradni blok", "construction"),
    ("insulation", "Toplotna izolacija", "construction"),
    ("floor_finish", "Podna obloga", "finish"),
    ("roof_cover", "Krovni pokrov", "roof"),
    ("roof_beam", "Krovna greda", "roof_structure"),
    ("ventilation_fan", "Ventilator", "ventilation"),
    ("heat_recovery_unit", "Rekuperator", "ventilation"),
    ("duct", "Ventilaciona cijev", "ventilation"),
    ("duct_elbow", "Koljeno", "ventilation"),
    ("plenum", "Plenum", "ventilation"),
    ("filter_g4", "G4 filter", "air_quality"),
    ("filter_f7", "F7 filter", "air_quality"),
)


def material_catalog() -> tuple[tuple[str, str, str], ...]:
    """Return the canonical starter catalog used by all downstream interfaces."""
    return MATERIAL_CATALOG
