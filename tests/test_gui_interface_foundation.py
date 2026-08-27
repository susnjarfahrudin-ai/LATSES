from lat_ces.gui_interface import InterfaceFoundation, TAB_OPTIONS, TABS


def test_interface_foundation_matches_top_level_contract():
    foundation = InterfaceFoundation()

    assert foundation.tabs == TABS
    assert foundation.tabs == (
        "MODEL OBJEKTA",
        "MATERIJAL OBJEKTA",
        "KONSTRUKCIJA OBJEKTA",
        "STATIKA OBJEKTA",
        "MEP OBJEKTA",
        "ILUSTRACIJA OBJEKTA",
        "MJERENJA U OBJEKTU",
    )
    assert foundation.left_panel == "TAB OPTIONS"
    assert foundation.center_panel == "REFERENCE HOUSE / WORKSPACE"
    assert foundation.right_panel == "KIŠOBRAN"
    assert foundation.natural_background is True
    assert foundation.model_first is True


def test_every_top_level_tab_has_context_options():
    assert set(TAB_OPTIONS) == set(TABS)
    assert all(TAB_OPTIONS[tab] for tab in TABS)


def test_core_physical_and_engineering_context_is_present():
    assert "Ploče" in TAB_OPTIONS["MATERIJAL OBJEKTA"]
    assert "Međuspratna konstrukcija" in TAB_OPTIONS["KONSTRUKCIJA OBJEKTA"]
    assert "Veze etaža" in TAB_OPTIONS["KONSTRUKCIJA OBJEKTA"]
    assert "Elektrika" in TAB_OPTIONS["MEP OBJEKTA"]
    assert "Akustika" in TAB_OPTIONS["MEP OBJEKTA"]
    assert "Svjetlost" in TAB_OPTIONS["MJERENJA U OBJEKTU"]
