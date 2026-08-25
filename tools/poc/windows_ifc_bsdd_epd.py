from __future__ import annotations

import json
import sys
import urllib.parse
import urllib.request
from pathlib import Path


def http_get(url: str, accept: str = "application/json") -> tuple[int, bytes]:
    request = urllib.request.Request(
        url,
        headers={"Accept": accept, "User-Agent": "LAT-CES-Windows-POC/0.1"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.status, response.read()


def main() -> int:
    result: dict[str, object] = {"python": sys.version, "checks": {}}

    try:
        import ifcopenshell  # type: ignore

        result["ifcopenshell_version"] = getattr(ifcopenshell, "version", "unknown")
        result["checks"]["ifcopenshell_import"] = True

        model = ifcopenshell.file(schema="IFC4")
        test_ifc = Path(__file__).with_name("generated_test.ifc")
        model.write(str(test_ifc))
        reopened = ifcopenshell.open(str(test_ifc))
        result["ifc_schema"] = reopened.schema
        result["checks"]["ifc_create_write_read"] = reopened.schema == "IFC4"
    except Exception as exc:
        result["checks"]["ifcopenshell_import"] = False
        result["checks"]["ifc_create_write_read"] = False
        result["ifcopenshell_error"] = repr(exc)
        print(json.dumps(result, indent=2))
        return 1

    # bSDD official non-secured Class API read. The URI is versioned and stable.
    try:
        bsdd_uri = "https://identifier.buildingsmart.org/uri/buildingsmart/ifc/4.3/class/IfcWall"
        query = urllib.parse.urlencode({"Uri": bsdd_uri})
        status, body = http_get(
            f"https://api.bsdd.buildingsmart.org/api/Class/v1?{query}"
        )
        result["bsdd_http_status"] = status
        result["bsdd_bytes"] = len(body)
        result["checks"]["bsdd_read"] = status == 200 and len(body) > 0
    except Exception as exc:
        result["checks"]["bsdd_read"] = False
        result["bsdd_error"] = repr(exc)

    # ÖKOBAUDAT official read interface. We deliberately do not redistribute its data
    # in this POC; we only prove that a packaged application can read the service.
    try:
        oekobau_url = "https://www.oekobaudat.de/OEKOBAU.DAT/resource/datastocks/"
        status, body = http_get(oekobau_url)
        result["oekobaudat_http_status"] = status
        result["oekobaudat_bytes"] = len(body)
        result["checks"]["oekobaudat_read"] = status == 200 and len(body) > 0
    except Exception as exc:
        result["checks"]["oekobaudat_read"] = False
        result["oekobaudat_error"] = repr(exc)

    data = Path(__file__).with_name("test_material.json")
    payload = json.loads(data.read_text(encoding="utf-8"))
    result["checks"]["fixture_load"] = bool(payload.get("dataset") and payload.get("materials"))
    result["dataset"] = payload.get("dataset")
    result["material_count"] = len(payload.get("materials", []))

    print(json.dumps(result, indent=2))
    return 0 if all(result["checks"].values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
