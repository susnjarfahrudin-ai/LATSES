from lat_ces.reference_house_workflow import build_reference_house_workflow


def test_every_reference_house_exterior_wall_has_room_adjacency() -> None:
    workflow = build_reference_house_workflow()
    model = workflow.model

    exterior_walls = [
        wall
        for level in model.levels.values()
        if level.floor_plan
        for wall in level.floor_plan.walls.values()
        if wall.exterior
    ]

    assert exterior_walls
    assert all(wall.room_ids for wall in exterior_walls)

    room_ids = {
        room.room_id
        for level in model.levels.values()
        for room in level.rooms.values()
    }
    assert all(set(wall.room_ids) <= room_ids for wall in exterior_walls)


def test_every_reference_house_room_touches_at_least_one_exterior_wall() -> None:
    workflow = build_reference_house_workflow()
    model = workflow.model

    rooms = [room for level in model.levels.values() for room in level.rooms.values()]
    exterior_wall_room_ids = {
        room_id
        for level in model.levels.values()
        if level.floor_plan
        for wall in level.floor_plan.walls.values()
        if wall.exterior
        for room_id in wall.room_ids
    }

    assert rooms
    assert {room.room_id for room in rooms} <= exterior_wall_room_ids


def test_adjacency_is_deterministic_for_reference_house() -> None:
    first = build_reference_house_workflow().model
    second = build_reference_house_workflow().model

    first_adjacency = [
        (level.name, wall.name, tuple(wall.room_ids))
        for level in first.levels.values()
        if level.floor_plan
        for wall in level.floor_plan.walls.values()
        if wall.exterior
    ]
    second_adjacency = [
        (level.name, wall.name, tuple(wall.room_ids))
        for level in second.levels.values()
        if level.floor_plan
        for wall in level.floor_plan.walls.values()
        if wall.exterior
    ]

    assert first_adjacency == second_adjacency
