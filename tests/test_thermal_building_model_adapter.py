from dataclasses import dataclass

from lat_ces.thermal import to_thermal_input


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


def test_thermal_uses_canonical_product_and_wall_identity():
    product = Product("product:block-25", "Example", "Block 25", (.25, .25, .30), .18, 800.0, 10.0)
    wall = Wall("wall-001", "room-hall", "room-kitchen", False, False, .25, product.product_id)
    model = Model((wall,), (product,))

    thermal = to_thermal_input(model)

    assert thermal.walls[0].wall_id == wall.wall_id
    assert thermal.walls[0].product_id == product.product_id
    assert thermal.walls[0].thermal_conductivity_w_mk == .18
    assert thermal.walls[0].conductive_resistance_m2kw == .25 / .18
