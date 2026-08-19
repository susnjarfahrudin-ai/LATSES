from lat_ces.building.geometry3d import LevelGeometry3D
from lat_ces.building.model import BuildingModel
from lat_ces.building.orientation import BuildingOrientation, CardinalDirection, ViewStyle
from lat_ces.building.section import SectionAxis, SectionDefinition, SectionView
from lat_ces.building.view3d import Model3DView


def test_orientation_exposes_cardinal_azimuths() -> None:
    orientation = BuildingOrientation(north_azimuth_deg=30.0)

    assert orientation.east_azimuth_deg == 120.0
    assert orientation.south_azimuth_deg == 210.0
    assert orientation.west_azimuth_deg == 300.0
    assert orientation.direction_for_azimuth(30.0) is CardinalDirection.NORTH
    assert orientation.direction_for_azimuth(120.0) is CardinalDirection.EAST


def test_building_model_owns_orientation() -> None:
    model = BuildingModel(name="Test")
    model.set_orientation(BuildingOrientation(north_azimuth_deg=15.0))

    assert model.orientation.north_azimuth_deg == 15.0


def test_section_supports_line_and_natural_views() -> None:
    geometry = LevelGeometry3D(level_id="L1", height=2.8, walls=())

    line_view = SectionView(
        definition=SectionDefinition(axis=SectionAxis.X, position_m=2.0, style=ViewStyle.CONSTRUCTIONAL_LINE),
        levels=(geometry,),
    )
    natural_view = SectionView(
        definition=SectionDefinition(axis=SectionAxis.Y, position_m=3.0, style=ViewStyle.NATURAL),
        levels=(geometry,),
    )

    assert line_view.is_line_based
    assert not line_view.is_natural
    assert natural_view.is_natural


def test_3d_view_supports_line_and_natural_styles() -> None:
    geometry = LevelGeometry3D(level_id="L1", height=2.8, walls=())

    line_view = Model3DView(levels=(geometry,), style=ViewStyle.CONSTRUCTIONAL_LINE)
    natural_view = Model3DView(levels=(geometry,), style=ViewStyle.NATURAL, show_materials=True)

    assert line_view.is_line_based
    assert not line_view.is_natural
    assert natural_view.is_natural
    assert natural_view.show_materials
