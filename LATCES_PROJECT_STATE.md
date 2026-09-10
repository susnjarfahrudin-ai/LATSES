# LAT-CES Project State — Reynolds GUI forensic checkpoint

## Current investigation status

**Scope:** READ-ONLY forensic investigation of GitHub Actions history/logs for `Reynolds` / `verify_gui_domain_access`. No source-code fix has been made.

### Exact Reynolds CI run
- Workflow: `Fahro Terenska Aplikacija - Installer`
- Run: **#17**
- Run ID: **33037789303**
- Job: `build-field-app-installer`
- Job ID: **98404288987**
- Branch: `fahro-terenska-aplikacija`
- Actual checkout HEAD: **`bcec0d7fb36d012b8379b2796b83d7239c3b7d64`**
- Commit message: `test(terenska): validate Reynolds GUI result semantics`
- Parent: `7005e4c129f11a6199016d0a5bfe45d50c93dd28`

### CI evidence
- Checkout succeeded and explicitly checked out `bcec0d7fb36d012b8379b2796b83d7239c3b7d64`.
- CPython **3.10.11** setup succeeded.
- Build dependencies installed successfully.
- Failure occurred in `Compile and verify field application`, inside `verify_all()` → `verify_gui_domain_access()`.
- The first concrete failure was: `assert reynolds_result and "GREŠKA:" not in reynolds_result`.
- Packaging/installer steps were skipped after this failure.
- Therefore this failure is **not evidence of a Python setup failure or an Actions SHA problem**.

## Exact GUI/Reynolds path on `bcec0d7`
`standalone_test/standalone_entry.py` contains `_run_reynolds()` calling `core.HardenedFluidMechanicsEngine.compute_reynolds_number()` with `self.fluid_density.value()`, `self.fluid_velocity.value()`, `self.fluid_length.value()`, and `self.fluid_viscosity.value()`.

On exception it executes `self.fluid_result.setPlainText(f"GREŠKA: {exc}")`.

The strengthened verification then strips `fluid_result`, rejects empty/`GREŠKA:` output, parses the numeric value after `:`, and requires `float(value_text) > 0.0`.

## GUI default Reynolds inputs found in source
At `bcec0d7`:
- density = **1000.0 kg/m³**
- velocity = **2.0 m/s**
- characteristic length = **0.05 m**
- dynamic viscosity intended value = **0.001 Pa·s**

The GUI creates the viscosity spin box and calls `setValue(0.001)` **before** `setDecimals(6)`.

## Reynolds engine
`HardenedFluidMechanicsEngine.compute_reynolds_number()` uses:
`Re = density_kg_m3 * velocity_m_s * characteristic_length_m / dynamic_visc_pa_s`

It rejects `dynamic_visc_pa_s <= 0` with `ValueError("Dynamic viscosity must be positive")`.

The same standalone verification suite explicitly checks:
`compute_reynolds_number(1000.0, 2.0, 0.05, 0.001) == 100000.0`.

Thus the mathematical inputs **1000, 2, 0.05, 0.001** yield **Re = 100000**; the formula itself is not implicated.

## Current hypothesis — NOT YET FINAL PROOF
A strong candidate is the PyQt6 `QDoubleSpinBox` precision/order: `setValue(0.001)` occurs before `setDecimals(6)`.

Possible mechanism:
- initial widget precision may quantize `0.001` to `0.00` when `setValue()` executes;
- subsequent `setDecimals(6)` changes precision but may not restore the original value;
- `_run_reynolds()` could therefore receive `dynamic_visc_pa_s == 0.0`;
- engine would raise `ValueError("Dynamic viscosity must be positive")`;
- `_run_reynolds()` would write `GREŠKA: Dynamic viscosity must be positive` to `fluid_result`;
- the strengthened assertion would then fail exactly as observed.

**Important:** this remains a strong inference until the actual runtime value of `self.fluid_viscosity.value()` or the actual exception text is directly observed.

## Next proof step — READ ONLY
Do NOT modify source code.

Establish one of:
1. direct runtime value of `self.fluid_viscosity.value()` on exact commit `bcec0d7`, or
2. exact runtime exception text written by `_run_reynolds()` / visible in the CI log.

Evidence sources:
- GitHub Actions run **33037789303**
- Job **98404288987**
- Commit **bcec0d7fb36d012b8379b2796b83d7239c3b7d64**
- `standalone_test/standalone_entry.py`
- `standalone_test/master_standalone.py`

## Important genealogy correction
Do **NOT** attribute the Reynolds CI run to commit `3d0c15d5aa5b088fddedd8056be724a2187f3fa1`. That commit is on a divergent line. The actual Reynolds run checked out `bcec0d7fb36d012b8379b2796b83d7239c3b7d64`.

## Working rule
First establish the actual runtime value/output. No fix, no PR modification, no architecture change, no Python/Actions upgrade, and no interpretation beyond the evidence until this proof step is complete.
