from lat_ces.catalog.product_binding import ensure_product_binding_registry
from lat_ces.reference_house_workflow import build_reference_house_workflow


def test_reference_house_seeds_canonical_wall_product_bindings():
    workflow = build_reference_house_workflow()
    registry = ensure_product_binding_registry(workflow.model)
    wall_ids = [
        wall.wall_id
        for level in workflow.model.levels.values()
        if level.floor_plan
        for wall in level.floor_plan.walls.values()
    ]
    assert wall_ids
    assert len(registry.all()) == len(wall_ids)
    assert all(registry.product_id_for(wall_id) == "MASONRY-THERMAL-25X25X30" for wall_id in wall_ids)


def test_reference_house_wall_material_uses_same_canonical_product_id():
    workflow = build_reference_house_workflow()
    products = {
        material.product_id
        for material in workflow.model.materials.values()
        if material.product_id
    }
    assert "MASONRY-THERMAL-25X25X30" in products
