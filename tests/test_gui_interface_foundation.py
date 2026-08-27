from lat_ces.gui_interface import InterfaceFoundation, TABS


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
