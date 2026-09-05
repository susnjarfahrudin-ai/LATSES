"""Canonical LAT-CES application service shared by CLI and GUI adapters."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Tuple

from lat_ces.rci_ad.observation import TelemetryObserver, observe_host_telemetry
from lat_ces.scientific.analysis.plenum import PlenumAnalysisEngine
from lat_ces.scientific.dimensions.dimension import DIMENSIONLESS, LENGTH, MASS, TIME
from lat_ces.scientific.quantity import PhysicalQuantity
from lat_ces.scientific.reports.exporter import SKOReportExporter
from lat_ces.scientific.reports.pdf_generator import SKOPDFGenerator
from lat_ces.scientific.units.units import Unit


def parse_quantity_dict(data: Dict[str, Any]) -> PhysicalQuantity:
    """Convert a JSON quantity dictionary into a PhysicalQuantity."""
    symbol = data.get("unit_symbol", data.get("symbol", "Pa"))
    dim_map = {
        "m/s": LENGTH / TIME,
        "kg/m3": MASS / (LENGTH**3),
        "kg/m³": MASS / (LENGTH**3),
        "Pa": MASS / (LENGTH * (TIME**2)),
        "m2": LENGTH**2,
        "m²": LENGTH**2,
        "m3/s": (LENGTH**3) / TIME,
        "m³/s": (LENGTH**3) / TIME,
        "-": DIMENSIONLESS,
    }
    dimension = dim_map.get(symbol, DIMENSIONLESS)
    unit = Unit(symbol, symbol, dimension)
    return PhysicalQuantity(
        value=float(data["value"]),
        uncertainty=float(data.get("uncertainty", 0.0)),
        unit=unit,
    )


def load_config(config_path: str | Path) -> Dict[str, Any]:
    """Load and decode a LAT-CES JSON analysis configuration."""
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Config file '{path}' does not exist.")
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def analyze_config(
    config: Dict[str, Any],
    *,
    project_default: str,
    plenum_default: str,
    equation_default: str,
    telemetry_observer: TelemetryObserver | None = None,
) -> Tuple[Any, SKOReportExporter]:
    """Run canonical analysis and optionally forward one host observation."""
    if telemetry_observer is not None:
        observe_host_telemetry(telemetry_observer)

    inputs = {
        name: parse_quantity_dict(quantity)
        for name, quantity in config.get("inputs", {}).items()
    }
    calculated = parse_quantity_dict(config["calculated_value"])
    limit = parse_quantity_dict(config["limit_value"])
    coverage_factor = float(config.get("coverage_factor", 2.0))

    safety_report = PlenumAnalysisEngine.evaluate_limit(
        calculated=calculated,
        limit=limit,
        coverage_factor=coverage_factor,
    )
    exporter = SKOReportExporter(
        project_name=config.get("project_name", project_default),
        engineer_name=config.get("engineer_name", "Engineer"),
        plenum_id=config.get("plenum_id", plenum_default),
        safety_report=safety_report,
        inputs=inputs,
        equation_name=config.get("equation_name", equation_default),
    )
    return safety_report, exporter


def export_report(exporter: SKOReportExporter, output_path: str | Path, report_format: str) -> Path:
    """Export a report through the canonical LAT-CES reporting layer."""
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    if report_format == "json":
        output.write_text(exporter.to_json(), encoding="utf-8")
    elif report_format == "md":
        output.write_text(exporter.to_markdown(), encoding="utf-8")
    elif report_format == "pdf":
        SKOPDFGenerator.generate_pdf(exporter, output)
    else:
        raise ValueError(f"Unsupported report format: {report_format}")
    return output
