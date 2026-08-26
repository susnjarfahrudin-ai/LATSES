from lat_ces.building_model.quantities import to_quantity_view
from lat_ces.gui_building_model import build_model_inspector_records
from lat_ces.reference_house_workflow import build_reference_house_workflow


def test_gui_inspector_reads_canonical_reference_house_identity():
    workflow = build_reference_house_workflow()
    records = build_model_inspector_records(workflow.model)

    kinds = {record["kind"] for record in records}
    assert {"level", "room", "wall", "opening", "stair", "terrace"}.issubset(kinds)

    kitchen = next(record for record in records if record["kind"] == "room" and record["name"] == "Kuhinja")
    assert kitchen["details"]["ID"] == kitchen["id"]
    assert kitchen["details"]["Površina"].endswith("m²")


def test_gui_inspector_uses_same_product_identity_as_quantity_view():
    workflow = build_reference_house_workflow()
    inspector = build_model_inspector_records(workflow.model)
    quantities = to_quantity_view(workflow.model)

    inspector_wall_ids = {record["details"]["ID"] for record in inspector if record["kind"] == "wall"}
    quantity_wall_ids = {record.wall_id for record in quantities.walls}
    assert inspector_wall_ids == quantity_wall_ids

    for wall in quantities.walls:
        inspector_record = next(record for record in inspector if record["kind"] == "wall" and record["id"] == wall.wall_id)
        assert inspector_record["details"]["Product ID"] == wall.product_id


def test_gui_inspector_does_not_mutate_model():
    workflow = build_reference_house_workflow()
    before = workflow.model.serialize()
    build_model_inspector_records(workflow.model)
    assert workflow.model.serialize() == before
