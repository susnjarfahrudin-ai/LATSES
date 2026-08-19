from lat_ces.building.interface_schema import BuildingStage, can_enter, stage_titles


def test_building_first_stage_order() -> None:
    assert stage_titles() == ("Krov", "Sprat", "Tlocrt", "Presjek", "3D")


def test_stage_prerequisites_are_sequential() -> None:
    assert can_enter(BuildingStage.ROOF, set())
    assert not can_enter(BuildingStage.LEVEL, set())
    assert can_enter(BuildingStage.LEVEL, {BuildingStage.ROOF})
    assert not can_enter(BuildingStage.FLOOR_PLAN, {BuildingStage.ROOF})
    assert can_enter(BuildingStage.FLOOR_PLAN, {BuildingStage.ROOF, BuildingStage.LEVEL})
    assert can_enter(
        BuildingStage.MODEL_3D,
        {
            BuildingStage.ROOF,
            BuildingStage.LEVEL,
            BuildingStage.FLOOR_PLAN,
            BuildingStage.SECTION,
        },
    )
