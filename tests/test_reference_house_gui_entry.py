from lat_ces.reference_house_workflow import build_reference_house_workflow


def test_reference_house_gui_workflow_loads_canonical_envelope():
    workflow = build_reference_house_workflow()

    assert workflow.current_step == 3
    assert len(workflow.model.levels) == 4
    assert workflow.model.roof is not None
    assert workflow.model.roof.roof_type == "dvovodni"
    assert all(level.length_m == 12.0 for level in workflow.model.levels.values())
    assert all(level.width_m == 10.0 for level in workflow.model.levels.values())
    assert all(level.height == 2.8 for level in workflow.model.levels.values())
    assert all(level.floor_plan is not None for level in workflow.model.levels.values())

    # Four exterior envelope walls remain canonical; internal room partitions
    # are additional walls owned by the same FloorPlan.
    assert all(
        sum(wall.exterior for wall in level.floor_plan.walls.values()) == 4
        for level in workflow.model.levels.values()
    )
    assert all(
        level.floor_plan.wall_count > 4
        for level in workflow.model.levels.values()
    )

    assert workflow.model.room_count > 0
    assert all(level.rooms for level in workflow.model.levels.values())
