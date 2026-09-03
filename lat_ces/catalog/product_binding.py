"""Canonical Product -> BuildingModel bindings.

The registry is owned by one BuildingModel instance. It stores only identity
links; engineering properties continue to live in the canonical product/material
records and scientific modules consume the same physical objects.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ProductBinding:
    target_id: str
    target_type: str
    product_id: str


class ProductBindingRegistry:
    def __init__(self) -> None:
        self.bindings: dict[str, ProductBinding] = {}

    def bind(self, target_id: str, target_type: str, product_id: str) -> ProductBinding:
        if not target_id.strip() or not product_id.strip() or not target_type.strip():
            raise ValueError("target_id, target_type and product_id are required")
        binding = ProductBinding(target_id=target_id, target_type=target_type, product_id=product_id)
        self.bindings[target_id] = binding
        return binding

    def get(self, target_id: str) -> ProductBinding | None:
        return self.bindings.get(target_id)

    def product_id_for(self, target_id: str) -> str | None:
        binding = self.get(target_id)
        return binding.product_id if binding else None

    def all(self) -> tuple[ProductBinding, ...]:
        return tuple(self.bindings.values())

    def to_dict(self) -> list[dict[str, str]]:
        return [{"target_id": b.target_id, "target_type": b.target_type, "product_id": b.product_id} for b in self.all()]

    @classmethod
    def from_dict(cls, data: list[dict[str, object]] | None) -> "ProductBindingRegistry":
        registry = cls()
        for item in data or []:
            registry.bind(str(item["target_id"]), str(item["target_type"]), str(item["product_id"]))
        return registry


def ensure_product_binding_registry(model: object) -> ProductBindingRegistry:
    registry = getattr(model, "product_bindings", None)
    if registry is None:
        registry = ProductBindingRegistry()
        setattr(model, "product_bindings", registry)
    if not isinstance(registry, ProductBindingRegistry):
        raise TypeError("BuildingModel.product_bindings must be a ProductBindingRegistry")
    return registry
