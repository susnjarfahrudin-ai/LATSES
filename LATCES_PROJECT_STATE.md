# LAT-CES Project State — Reynolds GUI forensic checkpoint

READ-ONLY forensic checkpoint. No Reynolds source-code fix has been made.

## Exact failing run
- Workflow: `Fahro Terenska Aplikacija - Installer`
- Run #17, ID `33037789303`
- Job `build-field-app-installer`, ID `98404288987`
- Branch: `fahro-terenska-aplikacija`
- Actual checkout: `bcec0d7fb36d012b8379b2796b83d7239c3b7d64`
- Commit: `test(terenska): validate Reynolds GUI result semantics`
- Parent: `7005e4c129f11a6199016d0a5bfe45d50c93dd28`

## Verified CI facts
Checkout, CPython 3.10.11 setup, and dependency installation all succeeded. The first concrete failure was in `verify_all()` → `verify_gui_domain_access()` at `assert reynolds_result and "GREŠKA:" not in reynolds_result`. Packaging/installer steps were skipped.

## Verified source path at exact commit
`_run_reynolds()` reads four GUI widget values and calls `HardenedFluidMechanicsEngine.compute_reynolds_number()`. On exception it writes `GREŠKA: {exc}` to `fluid_result`. The strengthened test rejects empty/error output, parses the numeric result, and requires it to be positive.

GUI defaults:
- density = 1000.0 kg/m³
- velocity = 2.0 m/s
- characteristic length = 0.05 m
- intended viscosity = 0.001 Pa·s

Viscosity widget order is `setValue(0.001)` followed by `setDecimals(6)`.

Engine formula: `Re = density * velocity * characteristic_length / dynamic_viscosity`. It raises `ValueError("Dynamic viscosity must be positive")` for viscosity <= 0. The same standalone suite verifies `Re(1000,2,0.05,0.001) == 100000.0`.

## Current hypothesis — unproven
The PyQt6 `QDoubleSpinBox` precision/order may quantize `0.001` before `setDecimals(6)`, causing `.value()` to be 0.0. That would yield `GREŠKA: Dynamic viscosity must be positive` and explain the exact assertion failure.

## NEXT ACTION — READ ONLY
Confirm the actual runtime `self.fluid_viscosity.value()` on `bcec0d7`, OR recover the exact exception text from the original Actions job log. No source/PR/GUI/architecture/Python/Actions changes until this is proven.

## Genealogy correction
Do not attribute the Reynolds run to `3d0c15d5aa5b088fddedd8056be724a2187f3fa1`; that line diverged. Actual run = `bcec0d7...`.

## Checkpoint
This document is a documentation-only continuity checkpoint on `main`; it does not change the Reynolds source branch.
