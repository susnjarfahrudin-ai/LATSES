"""Read-only scientific views over the canonical Building Model.

This module deliberately contains no duplicate Wall, Room, or Material model.
Views reference canonical object identities and expose only analysis data.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping


@dataclass(frozen=True)
class WallView:
    wall_id: str
    product_id: str
    room_ids: tuple[str, ...]
    thickness_m: float
    exterior: bool
    load_bearing: bool


@dataclass(frozen=True)
class MaterialView:
    product_id: str
    manufacturer: str
    name: str
    dimensions_m: tuple[float, float, float]
    thermal_conductivity_w_mk: float
    density_kg_m3: float
    compressive_strength_mpa: float


@dataclass(frozen=True)
class BuildingModelViews:
    """Immutable views; source objects remain owned by BuildingModel."""

    wall_views: tuple[WallView, ...]
    material_views: tuple[MaterialView, ...]

    def wall(self, wall_id: str) -> WallView:
        for view in self.wall_views:
            if view.wall_id == wall_id:
                return view
        raise KeyError(wall_id)

    def material(self, product_id: str) -> MaterialView:
        for view in self.material_views:
            if view.product_id == product_id:
                return view
        raise KeyError(product_id)


def build_read_only_views(model: Any) -> BuildingModelViews:
    """Project canonical model objects without creating scientific copies.

    The adapter accepts the existing model through duck typing so this contract
    can be introduced without changing the current BuildingModel API.
    """
    walls = getattr(model, "walls")
    products: Mapping[str, Any] = {
        product.product_id: product for product in getattr(model, "products")
    }

    wall_views = tuple(
        WallView(
            wall_id=wall.wall_id,
            product_id=wall.product_id,
            room_ids=tuple(x for x in (wall.room_a, wall.room_b) if x is not None),
            thickness_m=wall.thickness_m,
            exterior=wall.exterior,
            load_bearing=wall.load_bearing,
        )
        for wall in walls
    )
    material_views = tuple(
        MaterialView(
            product_id=product.product_id,
            manufacturer=product.manufacturer,
            name=product.name,
            dimensions_m=product.dimensions_m,
            thermal_conductivity_w_mk=product.thermal_conductivity_w_mk,
            density_kg_m3=product.density_kg_m3,
            compressive_strength_mpa=product.compressive_strength_mpa,
        )
        for product in products.values()
    )
    return BuildingModelViews(wall_views=wall_views, material_views=material_views)
