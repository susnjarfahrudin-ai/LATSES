from lat_ces.model_interface import has_interstorey_connection, model_sections


def test_model_contains_required_structure_sections():
    sections = model_sections()
    assert sections == (
        "Temelj",
        "Tlocrt",
        "Spratnost",
        "Prostorije",
        "Međuspratna ploča / plafon",
        "Orijentacija",
        "Krov",
    )


def test_model_requires_interstorey_connection():
    assert has_interstorey_connection() is True
