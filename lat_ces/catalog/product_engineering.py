"""Read-only engineering projection for Product -> BuildingModel bindings.

The projection consumes the canonical BuildingModel and existing structural/
thermal adapters. It does not create a second physical model or duplicate
engineering state.
"""
from __future__ import annotations

from dataclasses import dataclass

from lat_ces.building.structural import StructuralLoadReport, calculate_structural_loads
from lat_ces.catalog.product_binding import ProductBinding, ensure_product_binding_registry
from lat_ces.catalog.product_catalog import ProductSpec, get_product
from lat_ces.thermal.building_model_adapter import ThermalBuildingInput, to_thermal_input


@dataclass(frozen=True)
class ProductEngineeringRecord:
    target_id: str
    target_type: str
    product_id: str
    product_name: str
    manufacturer: str | None
    source: str | None
    verification_status: str
    density_kg_m3: float | None
    thermal_conductivity_w_mk: float | None
    structural_status: str
    self_weight_kn_m: float | None
    thermal_status: str
    conductive_resistance_m2kw: float | None
    findings: tuple[str, ...] = ()


@dataclass(frozen=True)
class ProductEngineeringReport:
    records: tuple[ProductEngineeringRecord, ...]

    @property
    def calculated_count(self) -> int:
        return sum(record.thermal_status == "CALCULATED" or record.structural_status == "CALCULATED" for record in self.records)

    @property
    def input_required_count(self) -> int:
        return sum("INPUT_REQUIRED" in (record.structural_status, record.thermal_status) or record.verification_status == "MISSING" for record in self.records)

    @property
    def status(self) -> str:
        if self.input_required_count:
            return "INPUT_REQUIRED"
        if self.records:
            return "CALCULATED"
        return "NO_PRODUCT_BINDINGS"


def _product_metadata(product_id: str) -> ProductSpec | None:
    return get_product(product_id)


def _binding_target(model, binding: ProductBinding):
    if binding.target_type == "wall":
        for level in model.levels.values():
            if level.floor_plan and binding.target_id in level.floor_plan.walls:
                return level, level.floor_plan.walls[binding.target_id]
    return None


def _thermal_map(thermal: ThermalBuildingInput):
    return {item.wall_id: item for item in thermal.walls}


def _record_for_binding(
    model,
    binding: ProductBinding,
    structural: StructuralLoadReport,
    thermal: ThermalBuildingInput,
) -> ProductEngineeringRecord:
    product = _product_metadata(binding.product_id)
    product_name = product.name if product else "UNKNOWN PRODUCT"
    manufacturer = product.manufacturer if product else None
    source = product.source if product else None
    verification_status = product.status if product else "MISSING"
    density = product.density_kg_m3 if product else None
    conductivity = product.thermal_conductivity_w_mk if product else None
    structural_status = "NOT_APPLICABLE"
    self_weight = None
    thermal_status = "NOT_APPLICABLE"
    resistance = None
    findings: list[str] = []

    target = _binding_target(model, binding)
    if binding.target_type == "wall" and target is not None:
        level, wall = target
        material = model.materials.get(wall.material_id) if wall.material_id else None
        if material is not None:
            density = material.density if material.density is not None else density
            conductivity = material.thermal_conductivity if material.thermal_conductivity is not None else conductivity
            if product is None:
                product_name = material.name
                manufacturer = material.manufacturer
        structural_wall = next((item for item in structural.walls if item.wall_id == wall.wall_id), None)
        if structural_wall is not None:
            structural_status = "CALCULATED"
            self_weight = structural_wall.self_weight_kn_m
        elif wall.load_bearing and wall.tributary_width_m <= 0.0:
            structural_status = "INPUT_REQUIRED"
            findings.append("unesena tributarna širina zida")
        elif wall.load_bearing and density is None:
            structural_status = "INPUT_REQUIRED"
            findings.append("nedostaje gustina materijala")
        elif not wall.load_bearing:
            structural_status = "NOT_LOAD_BEARING"
        else:
            structural_status = "INPUT_REQUIRED"

        thermal_wall = _thermal_map(thermal).get(wall.wall_id)
        if thermal_wall is not None and conductivity is not None and conductivity > 0:
            thermal_status = "CALCULATED"
            resistance = round(wall.thickness / conductivity, 6)
        else:
            thermal_status = "INPUT_REQUIRED"
            findings.append("nedostaje λ (toplotna provodljivost)")

    if not product:
        findings.append("proizvod nije pronađen u canonical katalogu")
        if binding.target_type == "wall":
            structural_status = "INPUT_REQUIRED"
            thermal_status = "INPUT_REQUIRED"

    return ProductEngineeringRecord(
        target_id=binding.target_id,
        target_type=binding.target_type,
        product_id=binding.product_id,
        product_name=product_name,
        manufacturer=manufacturer,
        source=source,
        verification_status=verification_status,
        density_kg_m3=density,
        thermal_conductivity_w_mk=conductivity,
        structural_status=structural_status,
        self_weight_kn_m=self_weight,
        thermal_status=thermal_status,
        conductive_resistance_m2kw=resistance,
        findings=tuple(dict.fromkeys(findings)),
    )


def build_product_engineering_report(model) -> ProductEngineeringReport:
    """Build a deterministic Product -> Statics/Thermal read-only projection."""
    bindings = ensure_product_binding_registry(model)
    structural = calculate_structural_loads(model)
    thermal = to_thermal_input(model)
    report = ProductEngineeringReport(
        records=tuple(_record_for_binding(model, binding, structural, thermal) for binding in bindings.all())
    )
    model.product_engineering_report = report
    return report


__all__ = [
    "ProductEngineeringRecord",
    "ProductEngineeringReport",
    "build_product_engineering_report",
]
