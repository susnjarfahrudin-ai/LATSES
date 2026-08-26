from lat_ces.building_model.quantities import to_quantity_view
from lat_ces.gui_building_model import build_model_inspector_records
from lat_ces.reference_house_workflow import build_reference_house_workflow


def test_gui_inspector_reads_canonical_reference_house_identity():
    workflow = build_reference_house_workflow()
    records = build_model_inspector_records(workflow.model)

    kinds = {record["kind"] for record in records}
    assert {"level", "room", "wall", "opening", "material"}.issubset(kinds)
    assert "stair" not in kinds
    assert "terrace" not in kinds

    level = next(record for record in records if record["kind"] == "level")
    assert level["details"]["ID"] == level["id"]
    assert level["details"]["Visina"].endswith("m")

    room = next(record for record in records if record["kind"] == "room")
    assert room["details"]["ID"] == room["id"]
    assert room["details"]["Naziv"]

    opening = next(record for record in records if record["kind"] == "opening")
    assert opening["details"]["ID"] == opening["id"]
    assert opening["details"]["Tip"] in {"door", "window"}


def test_gui_inspector_uses_same_product_identity_as_quantity_view():
    workflow = build_reference_house_workflow()
    inspector = build_model_inspector_records(workflow.model)
    quantities = to_quantity_view(workflow.model)

    inspector_wall_ids = {record["details"]["ID"] for record in inspector if record["kind"] == "wall"}
    quantity_wall_ids = {record.wall_id for record in quantities.walls}
    assert inspector_wall_ids == quantity_wall_ids

    for wall in quantities.walls:
        inspector_record = next(record for record in inspector if record["kind"] == "wall" and record["id"] == wall.wall_id)
        assert inspector_record["details"]["Product ID"] == (wall.product_id or "N/A")


def test_gui_inspector_does_not_mutate_model():
    workflow = build_reference_house_workflow()
    model = workflow.model
    before = (model.model_id, model.room_count, len(model.materials), tuple(model.levels))
    build_model_inspector_records(model)
    after = (model.model_id, model.room_count, len(model.materials), tuple(model.levels))
    assert after == before
