"""Minimal MODEL interface contract for the new LAT-CES GUI foundation."""

MODEL_SECTIONS = (
    "Temelj",
    "Tlocrt",
    "Spratnost",
    "Prostorije",
    "Međuspratna ploča / plafon",
    "Orijentacija",
    "Krov",
)


def model_sections() -> tuple[str, ...]:
    """Return MODEL sections in their canonical interface order."""
    return MODEL_SECTIONS


def has_interstorey_connection() -> bool:
    """The MODEL contract explicitly includes the interstorey connection."""
    return "Međuspratna ploča / plafon" in MODEL_SECTIONS
