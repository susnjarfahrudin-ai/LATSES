import ast
import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
PRODUCTION_ROOT = REPO_ROOT / "lat_ces"
LEGACY_ROOT = PRODUCTION_ROOT / "modules"


def _imported_module_names(node: ast.AST) -> list[str]:
    if isinstance(node, ast.Import):
        return [alias.name for alias in node.names]
    if isinstance(node, ast.ImportFrom):
        if node.level:
            return []
        return [node.module or ""]
    return []


def test_production_code_does_not_introduce_legacy_module_imports():
    violations = []

    for path in PRODUCTION_ROOT.rglob("*.py"):
        if LEGACY_ROOT in path.parents:
            continue
        if "tests" in path.parts:
            continue

        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            for module_name in _imported_module_names(node):
                if module_name == "lat_ces.modules" or module_name.startswith("lat_ces.modules."):
                    violations.append(f"{path.relative_to(REPO_ROOT)}:{node.lineno}: {module_name}")

    assert not violations, "Production code must not introduce legacy imports:\n" + "\n".join(violations)


def test_legacy_quantity_module_is_retired():
    assert importlib.util.find_spec("lat_ces.modules.quantity") is None


def test_canonical_physical_quantity_is_available():
    from lat_ces.scientific.quantity import PhysicalQuantity

    assert PhysicalQuantity is not None
