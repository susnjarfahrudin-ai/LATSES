# LAT-CES Project State — Reynolds GUI forensic checkpoint

**Scope:** READ-ONLY forensic investigation of the Reynolds GUI failure. No Reynolds source-code fix.

## Exact failing run
Workflow `Fahro Terenska Aplikacija - Installer`, run #17 (`33037789303`), job `build-field-app-installer` (`98404288987`), branch `fahro-terenska-aplikacija`, checkout `bcec0d7fb36d012b8379b2796b83d7239c3b7d64` (`test(terenska): validate Reynolds GUI result semantics`), parent `7005e4c129f11a6199016d0a5bfe45d50c93dd28`.

## Verified
- Checkout succeeded.
- CPython 3.10.11 setup succeeded.
- Dependencies installed.
- First concrete failure: `verify_all()` → `verify_gui_domain_access()` → `assert reynolds_result and "GREŠKA:" not in reynolds_result`.
- `_run_reynolds()` passes density, velocity, characteristic length and viscosity widget values to the Reynolds engine; exceptions are written to `fluid_result` as `GREŠKA: {exc}`.
- GUI intended defaults: 1000 kg/m³, 2 m/s, 0.05 m, 0.001 Pa·s.
- Engine formula: `Re = density * velocity * length / viscosity`; viscosity <= 0 raises `ValueError("Dynamic viscosity must be positive")`.
- Non-GUI suite verifies `Re(1000,2,0.05,0.001) == 100000.0`.
- Viscosity widget calls `setValue(0.001)` before `setDecimals(6)`.

## Hypothesis — NOT PROVEN
PyQt6 spin-box precision/order may quantize 0.001 to 0.0 before precision is changed, causing the engine error and the observed assertion failure.

## Next proof step — READ ONLY
Recover the exact runtime viscosity value or exact exception text from the original Actions log for job `98404288987`. Do not change source, PR, GUI, architecture, Python, Actions, limiter, or RCI-AD until proven.

## Genealogy correction
The Reynolds run is NOT `3d0c15d5...`; that line diverged. Actual Reynolds run is `bcec0d7...`.

This file is only a continuity checkpoint on `main`; it does not alter the Reynolds source branch.
