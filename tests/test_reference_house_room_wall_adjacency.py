from lat_ces.reference_house_workflow import build_reference_house_workflow


def test_every_reference_house_room_touches_at_least_one_exterior_wall() -> None:
    workflow = build_reference_house_workflow()
    model = workflow.model

    room_names = {
        room.room_id: (level.name, room.name)
        for level in model.levels.values()
        for room in level.rooms.values()
        if room.footprint.height > 0
    }
    adjacent_room_ids = {
        room_id
        for level in model.levels.values()
        if level.floor_plan
        for wall in level.floor_plan.walls.values()
        if wall.exterior
        for room_id in wall.room_ids
    }

    assert room_names
    assert set(room_names) <= adjacent_room_ids


def test_reference_house_exterior_wall_bindings_reference_only_existing_rooms() -> None:
    workflow = build_reference_house_workflow()
    model = workflow.model

    room_ids = {
        room.room_id
        for level in model.levels.values()
        for room in level.rooms.values()
        if room.footprint.height > 0
    }
    exterior_walls = [
        wall
        for level in model.levels.values()
        if level.floor_plan
        for wall in level.floor_plan.walls.values()
        if wall.exterior
    ]

    assert exterior_walls
    assert all(set(wall.room_ids) <= room_ids for wall in exterior_walls)


def test_reference_house_adjacency_is_deterministic_by_room_name() -> None:
    first = build_reference_house_workflow().model
    second = build_reference_house_workflow().model

    def signature(model):
        room_name_by_id = {
            room.room_id: room.name
            for level in model.levels.values()
            for room in level.rooms.values()
            if room.footprint.height > 0
        }
        return [
            (level.name, wall.name, tuple(sorted(room_name_by_id[room_id] for room_id in wall.room_ids)))
            for level in model.levels.values()
            if level.floor_plan
            for wall in level.floor_plan.walls.values()
            if wall.exterior
        ]

    assert signature(first) == signature(second)
