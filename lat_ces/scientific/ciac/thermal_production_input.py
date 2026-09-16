from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from lat_ces.catalog.product_catalog import ProductSpec
from lat_ces.scientific.ciac.thermal_vertical import (
    Admission,
    CalculationContext,
    admit_thermal_conductivity,
)
from lat_ces.scientific.evidence.property_instance import PropertyInstance
from lat_ces.scientific.evidence_state import EvidenceState


@dataclass(frozen=True)
class ThermalPropertyAdmission:
    """One admitted thermal-conductivity input for a concrete wall context."""

    instance: PropertyInstance
    admission: Admission


def material_thermal_conductivity_instance(wall: Any, material: Any) -> PropertyInstance:
    """Represent the actual user-declared Material lambda without inventing provenance."""
    material_id = str(material.material_id)
    wall_id = str(wall.wall_id)
    return PropertyInstance(
        property_id="thermal_conductivity",
        subject_id=wall_id,
        value=material.thermal_conductivity,
        unit="W/mK",
        source="USER_DECLARED",
        provenance="GUI_MATERIAL_ENTRY",
        scope="BuildingModel.Material",
        evidence_id=f"DECLARED:{material_id}:thermal_conductivity:r1",
        evidence_state=EvidenceState.DECLARED,
    )


def product_thermal_conductivity_instance(wall: Any, product: ProductSpec) -> PropertyInstance | None:
    """Represent catalog lambda while preserving the catalog's source metadata."""
    if product.thermal_conductivity_w_mk is None:
        return None
    return PropertyInstance(
        property_id="thermal_conductivity",
        subject_id=str(wall.wall_id),
        value=product.thermal_conductivity_w_mk,
        unit="W/mK",
        source=product.source or "PRODUCT_CATALOG",
        provenance=product.source_document or f"ProductCatalog:{product.product_id}",
        scope="ProductCatalog",
        evidence_id=product.evidence_id or f"CATALOG:{product.product_id}",
        evidence_state=EvidenceState.UNKNOWN,
    )


def admit_wall_thermal_conductivity(
    wall: Any,
    instance: PropertyInstance,
) -> ThermalPropertyAdmission:
    """Apply the existing isolated CIAC admission contract at the production input boundary."""
    context = CalculationContext(
        context_id=f"thermal-room-wall:{wall.wall_id}",
        property_id="thermal_conductivity",
        subject_id=str(wall.wall_id),
        unit="W/mK",
        purpose="opaque exterior wall transmission heat loss",
    )
    admission = admit_thermal_conductivity(instance, context)
    return ThermalPropertyAdmission(instance=instance, admission=admission)


__all__ = [
    "ThermalPropertyAdmission",
    "material_thermal_conductivity_instance",
    "product_thermal_conductivity_instance",
    "admit_wall_thermal_conductivity",
]
