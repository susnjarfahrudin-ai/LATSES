"""Blender-side reconstruction and measurement for LAT-CES scene v1."""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector


def _arguments() -> tuple[Path, Path, Path]:
    args = sys.argv
    if "--" not in args:
        raise SystemExit("expected arguments after --")
    values = args[args.index("--") + 1 :]
    if len(values) != 3:
        raise SystemExit("expected scene.json blend_path measurement.json")
    return Path(values[0]), Path(values[1]), Path(values[2])


def _clear_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)


def _wall_geometry(scene: dict) -> dict[str, dict]:
    expected: dict[str, dict] = {}
    for level in scene["levels"]:
        for wall in level["walls"]:
            placement = wall.get("placement")
            if placement is None:
                continue
            dx = placement["x2_m"] - placement["x1_m"]
            dy = placement["y2_m"] - placement["y1_m"]
            length = math.hypot(dx, dy)
            if not math.isclose(length, wall["length_m"], abs_tol=1e-9):
                raise ValueError(f"authoritative length mismatch for {wall['id']}")
            angle = math.atan2(dy, dx)
            bpy.ops.mesh.primitive_cube_add(location=(
                (placement["x1_m"] + placement["x2_m"]) / 2.0,
                (placement["y1_m"] + placement["y2_m"]) / 2.0,
                wall["height_m"] / 2.0,
            ))
            obj = bpy.context.object
            obj.name = f"wall:{wall['id']}"
            obj.rotation_euler[2] = angle
            obj.scale = (
                wall["length_m"] / 2.0,
                wall["thickness_m"] / 2.0,
                wall["height_m"] / 2.0,
            )
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
            obj["latces_id"] = wall["id"]
            obj["latces_source"] = scene["source"]
            obj["latces_schema"] = scene["schema"]
            obj["latces_opening_count"] = len(wall["openings"])
            expected[wall["id"]] = {
                "p1": (placement["x1_m"], placement["y1_m"], 0.0),
                "p2": (placement["x2_m"], placement["y2_m"], 0.0),
                "length_m": wall["length_m"],
                "thickness_m": wall["thickness_m"],
                "height_m": wall["height_m"],
                "opening_count": len(wall["openings"]),
            }
    return expected


def _measure(expected: dict[str, dict]) -> list[dict]:
    checks: list[dict] = []
    mesh_objects = [obj for obj in bpy.context.scene.objects if obj.type == "MESH"]
    by_id = {obj.get("latces_id"): obj for obj in mesh_objects}
    checks.append({"name": "mesh_count", "status": "PASS" if len(mesh_objects) == len(expected) else "FAIL", "actual": len(mesh_objects), "expected": len(expected)})

    for wall_id, exp in expected.items():
        obj = by_id.get(wall_id)
        if obj is None:
            checks.append({"name": f"identity:{wall_id}", "status": "FAIL", "reason": "missing mesh"})
            continue

        xs = [v.co.x for v in obj.data.vertices]
        ys = [v.co.y for v in obj.data.vertices]
        zs = [v.co.z for v in obj.data.vertices]
        local_dims = (max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs))
        expected_dims = (exp["length_m"], exp["thickness_m"], exp["height_m"])
        dimension_errors = tuple(a - b for a, b in zip(local_dims, expected_dims))
        checks.append({
            "name": f"dimensions:{wall_id}",
            "status": "PASS" if all(math.isclose(a, b, abs_tol=1e-9) for a, b in zip(local_dims, expected_dims)) else "FAIL",
            "actual": local_dims,
            "expected": expected_dims,
            "error": dimension_errors,
            "abs_error": tuple(abs(value) for value in dimension_errors),
            "max_abs_error": max(abs(value) for value in dimension_errors),
        })

        p1 = obj.matrix_world @ Vector((-exp["length_m"] / 2.0, 0.0, 0.0))
        p2 = obj.matrix_world @ Vector((exp["length_m"] / 2.0, 0.0, 0.0))
        measured_endpoints = ((p1.x, p1.y), (p2.x, p2.y))
        expected_endpoints = ((exp["p1"][0], exp["p1"][1]), (exp["p2"][0], exp["p2"][1]))
        endpoint_errors = tuple(
            tuple(actual - expected for actual, expected in zip(pair_a, pair_b))
            for pair_a, pair_b in zip(measured_endpoints, expected_endpoints)
        )
        endpoint_abs_errors = tuple(
            tuple(abs(value) for value in pair) for pair in endpoint_errors
        )
        endpoint_max_abs_error = max(value for pair in endpoint_abs_errors for value in pair)
        endpoint_ok = endpoint_max_abs_error <= 1e-9
        checks.append({
            "name": f"endpoints:{wall_id}",
            "status": "PASS" if endpoint_ok else "FAIL",
            "actual": measured_endpoints,
            "expected": expected_endpoints,
            "error": endpoint_errors,
            "abs_error": endpoint_abs_errors,
            "max_abs_error": endpoint_max_abs_error,
        })

        checks.append({"name": f"opening_metadata:{wall_id}", "status": "PASS" if obj.get("latces_opening_count") == exp["opening_count"] else "FAIL", "actual": obj.get("latces_opening_count"), "expected": exp["opening_count"]})

    return checks


def main() -> int:
    scene_path, blend_path, report_path = _arguments()
    scene = json.loads(scene_path.read_text(encoding="utf-8"))
    _clear_scene()
    expected = _wall_geometry(scene)
    checks = _measure(expected)
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))
    report = {
        "renderer": "Blender",
        "schema": scene["schema"],
        "source": scene["source"],
        "checks": checks,
        "mesh_objects": sum(obj.type == "MESH" for obj in bpy.context.scene.objects),
        "note": "Wall solids are measured. Opening geometry is not cut in this first POC; opening count is preserved as metadata.",
    }
    report_path.write_text(json.dumps(report, sort_keys=True, indent=2), encoding="utf-8")
    return 0 if all(item["status"] == "PASS" for item in checks) else 1


if __name__ == "__main__":
    raise SystemExit(main())
