from lat_ces.building.orientation import ViewStyle
from lat_ces.gui import STEPS, LATCESApp


def test_gui_exposes_canonical_building_view_sequence() -> None:
    assert STEPS == ((1, "Krov"), (2, "Sprat"), (3, "Tlocrt"), (4, "Presjek"), (5, "3D"))


def test_gui_imports_without_creating_a_window() -> None:
    assert LATCESApp is not None
    assert ViewStyle.CONSTRUCTIONAL_LINE.value == "constructional_line"
    assert ViewStyle.NATURAL.value == "natural"
