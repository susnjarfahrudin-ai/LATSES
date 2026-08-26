from dataclasses import dataclass

from lat_ces.building_model.source_of_truth import build_read_only_views


@dataclass(frozen=True)
class Product:
    product_id: str
    manufacturer: str
    name: str
    dimensions_m: tuple[float, float, float]
    thermal_conductivity_w_mk: float
    density_kg_m3: float
    compressive_strength_mpa: float


@dataclass(frozen=True)
class Wall:
    wall_id: str
    room_a: str
    room_b: str | None
    exterior: bool
    load_bearing: bool
    thickness_m: float
    product_id: str


@dataclass(frozen=True)
class Model:
    walls: tuple[Wall, ...]
    products: tuple[Product, ...]


def test_scientific_views_preserve_canonical_identities():
    product = Product("product:block-25", "Example", "Block 25", (.25, .25, .30), .18, 800.0, 10.0)
    wall = Wall("wall-001", "room-hall", "room-kitchen", False, False, .25, product.product_id)
    model = Model((wall,), (product,))

    views = build_read_only_views(model)

    assert views.wall_views[0].wall_id == wall.wall_id
    assert views.wall_views[0].product_id == product.product_id
    assert views.material_views[0].product_id == product.product_id
    assert views.wall_views[0].room_ids == ("room-hall", "room-kitchen")


def test_scientific_views_are_immutable():
    product = Product("product:block-25", "Example", "Block 25", (.25, .25, .30), .18, 800.0, 10.0)
    wall = Wall("wall-001", "room-hall", None, True, True, .25, product.product_id)
    views = build_read_only_views(Model((wall,), (product,)))

    try:
        views.wall_views[0].wall_id = "different"
    except Exception:
        pass
    else:
        raise AssertionError("scientific views must be immutable")

    assert views.wall_views[0].wall_id == "wall-001"
