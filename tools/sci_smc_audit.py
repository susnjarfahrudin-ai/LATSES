"""Read-only SCI/legacy/SMC inventory generator.

Run from repository root. It never edits source files. It reports exact files that
exist, import references, and candidate consolidation actions. Human acceptance
remains required for RETIRE and RELEASE.
"""
from __future__ import annotations

import ast
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
DECISIONS = {"KEEP", "MERGE", "ADAPT", "MOVE", "RETIRE", "NEW"}


def python_files():
    return sorted(ROOT.glob("**/*.py"))


def imports(path: pathlib.Path):
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (SyntaxError, UnicodeDecodeError):
        return []
    out = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            out.extend(a.name for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            out.append(node.module)
    return out


def main():
    files = python_files()
    print(f"PYTHON_FILES={len(files)}")
    print("LEGACY_BUILD_FILES=")
    for path in files:
        if path.name.startswith("build_mod"):
            print(path.relative_to(ROOT))
    print("SCIENTIFIC_FILES=")
    for path in files:
        if "lat_ces/scientific" in path.as_posix():
            print(path.relative_to(ROOT))
    print("IMPORT_GRAPH_SAMPLES=")
    for path in files:
        if path.name in {"sko.py", "dimension.py", "quantity.py", "measurement.py", "registry.py"}:
            print(path.relative_to(ROOT), "->", ", ".join(imports(path)))
    print("DECISION_VOCABULARY=", ",".join(sorted(DECISIONS)))


if __name__ == "__main__":
    main()
