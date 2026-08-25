from __future__ import annotations

import importlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "docs" / "SCI_1_145_ACCEPTANCE_MATRIX.json"


def parse_range(value: str) -> set[int]:
    start, end = (int(x) for x in value.split("-", 1))
    return set(range(start, end + 1))


def main() -> None:
    data = json.loads(MATRIX.read_text(encoding="utf-8"))
    expected = set(range(2, 146))
    covered: set[int] = set()
    for group in data["groups"]:
        covered |= parse_range(group["range"])
        module = group["module"].split(" + ")[0].strip()
        if module.startswith("lat_ces."):
            importlib.import_module(module)
        test_path = ROOT / group["test"]
        if not test_path.exists():
            raise SystemExit(f"SCI acceptance test path missing: {test_path}")
    if covered != expected:
        raise SystemExit(f"SCI coverage mismatch: missing={sorted(expected-covered)} extra={sorted(covered-expected)}")
    if data.get("status_on_branch") != "PENDING_CI":
        raise SystemExit("Acceptance matrix may only use PENDING_CI before merge")
    text = (ROOT / "lat_ces" / "scientific" / "core" / "governance.py").read_text(encoding="utf-8")
    required_symbols = (
        "class ScientificArtifact",
        "class EvolutionEngine",
        "class GovernanceEngine",
        "class PreservationEngine",
        "class IntegrityTrustEngine",
        "class AssuranceEngine",
        "class LifecycleEngine",
        "class EcosystemEngine",
        "class IntelligenceEngine",
        "class FederationEngine",
        "class SecurityGovernanceEngine",
        "class AdaptiveSecurityGovernance",
    )
    missing = [symbol for symbol in required_symbols if symbol not in text]
    if missing:
        raise SystemExit(f"Canonical scientific governance layer is incomplete: {missing}")
    print(f"SCI acceptance structure OK: {len(expected)} SCI items + LAT-SCOPE-0001 covered")


if __name__ == "__main__":
    main()
