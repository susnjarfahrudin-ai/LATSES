from lat_ces.reference_house_workflow import build_reference_house_workflow


def test_reference_house_populates_authoritative_room_identities():
    workflow = build_reference_house_workflow()
    model = workflow.model

    assert len(model.levels) == 4
    room_names = [room.name for level in model.levels.values() for room in level.rooms.values()]
    assert "Hodnik" in room_names
    assert "Kuhinja + trpezarija" in room_names
    assert "Dnevni boravak" in room_names
    assert "Gostinska soba" in room_names


def test_reference_house_rooms_preserve_source_areas_and_heights():
    workflow = build_reference_house_workflow()
    model = workflow.model
    ground = next(level for level in model.levels.values() if level.name == "Prizemlje")
    areas = {room.name: room.floor_area for room in ground.rooms.values()}

    assert areas["Dnevni boravak"] == 30.0
    assert areas["Kuhinja + trpezarija"] == 22.0
    assert all(room.footprint.height == 2.8 for room in ground.rooms.values())


def test_reference_house_has_canonical_openings_and_product_identity():
    workflow = build_reference_house_workflow()
    model = workflow.model
    assert len(model.materials) == 1

    openings = [
        opening
        for level in model.levels.values()
        if level.floor_plan
        for wall in level.floor_plan.walls.values()
        for opening in wall.openings
    ]
    assert any(opening.kind == "door" for opening in openings)
    assert any(opening.kind == "window" for opening in openings)

    for level in model.levels.values():
        assert level.floor_plan is not None
        assert all(wall.material_id is not None for wall in level.floor_plan.walls.values())


def test_reference_house_respects_load_bearing_policy():
    workflow = build_reference_house_workflow()
    for level in workflow.model.levels.values():
        assert level.floor_plan is not None
        assert all(wall.load_bearing for wall in level.floor_plan.walls.values())
        assert all(
            (not wall.load_bearing) or wall.tributary_width_m > 0.0
            for wall in level.floor_plan.walls.values()
        )
