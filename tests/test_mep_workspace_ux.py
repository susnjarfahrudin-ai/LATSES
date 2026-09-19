from lat_ces.catalog.product_catalog import products_for_category


def test_mep_has_floor_build_up_choice_categories():
    assert {p.product_id for p in products_for_category("Estrih")} >= {
        "ESTRICH-CEMENT-50",
        "ESTRICH-ANHYDRITE-50",
    }
    assert {p.product_id for p in products_for_category("Završni sloj")} >= {
        "FINISH-CERAMIC-GRES-10",
        "FINISH-LAMINATE-10",
        "FINISH-PARKET-15",
    }


def test_floor_finish_choices_are_explicit_reference_inputs():
    for product in products_for_category("Završni sloj"):
        assert product.status == "REFERENCE"
        assert product.source
