"""Final SMC consolidation guards for canonical import ownership."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GUARD_PATH = Path(__file__).resolve()

LEGACY_IMPORTS = (
    "lat_ces.modules.quantity",
    "lat_ces.modules.equation",
)

# The guard protects production/source ownership. Tests may intentionally mention
# retired import paths to prove that the retirement itself is enforced.
EXCLUDED_DIRS = {".git", ".pytest_cache", "build", "dist", "__pycache__", "tests"}


def _source_files():
    for path in ROOT.rglob("*.py"):
        if path == GUARD_PATH or any(part in EXCLUDED_DIRS for part in path.parts):
            continue
        yield path


def test_no_retired_quantity_or_equation_imports_remain():
    offenders = []
    for path in _source_files():
        text = path.read_text(encoding="utf-8")
        for legacy in LEGACY_IMPORTS:
            if legacy in text:
                offenders.append(f"{path}: {legacy}")
    assert not offenders, "Retired legacy imports remain:\n" + "\n".join(offenders)


def test_scientific_units_are_compatibility_facades_only():
    for path in (
        ROOT / "lat_ces" / "scientific" / "units" / "unit.py",
        ROOT / "lat_ces" / "scientific" / "units" / "quantity.py",
    ):
        if path.exists():
            text = path.read_text(encoding="utf-8").lower()
            assert "compatibility facade" in text


def test_canonical_scientific_quantity_exists():
    canonical = ROOT / "lat_ces" / "scientific" / "quantity" / "quantity.py"
    assert canonical.exists()


def test_smc_contract_and_registry_exist():
    assert (ROOT / "lat_ces" / "scientific" / "smc" / "contracts.py").exists()
    assert (ROOT / "lat_ces" / "scientific" / "smc" / "registry.py").exists()
