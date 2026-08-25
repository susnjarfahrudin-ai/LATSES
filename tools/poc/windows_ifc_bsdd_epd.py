from __future__ import annotations

import json
import sys
from pathlib import Path


def main() -> int:
    result: dict[str, object] = {"python": sys.version, "checks": {}}

    try:
        import ifcopenshell  # type: ignore
        result["ifcopenshell_version"] = getattr(ifcopenshell, "version", "unknown")
        result["checks"]["ifcopenshell_import"] = True
    except Exception as exc:
        result["checks"]["ifcopenshell_import"] = False
        result["ifcopenshell_error"] = repr(exc)
        print(json.dumps(result, indent=2))
        return 1

    # bSDD is tested through IfcOpenShell's optional API surface when present.
    try:
        import ifcopenshell.api  # noqa: F401
        result["checks"]["ifcopenshell_api_import"] = True
    except Exception as exc:
        result["checks"]["ifcopenshell_api_import"] = False
        result["ifcopenshell_api_error"] = repr(exc)

    data = Path(__file__).with_name("test_material.json")
    payload = json.loads(data.read_text(encoding="utf-8"))
    result["checks"]["epd_dataset_load"] = bool(payload.get("dataset") and payload.get("materials"))
    result["dataset"] = payload.get("dataset")
    result["material_count"] = len(payload.get("materials", []))

    print(json.dumps(result, indent=2))
    return 0 if all(result["checks"].values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
