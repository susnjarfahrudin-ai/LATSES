# LAT-CES Project State — Reynolds GUI forensic checkpoint

READ-ONLY forensic investigation; no Reynolds source-code fix.

Exact failing run: `Fahro Terenska Aplikacija - Installer` #17, run `33037789303`, job `build-field-app-installer` `98404288987`, branch `fahro-terenska-aplikacija`, checkout `bcec0d7fb36d012b8379b2796b83d7239c3b7d64`, parent `7005e4c129f11a6199016d0a5bfe45d50c93dd28`.

Verified: checkout, CPython 3.10.11 and dependencies succeeded. First concrete failure: `verify_all()` → `verify_gui_domain_access()` at `assert reynolds_result and "GREŠKA:" not in reynolds_result`.

Exact source path: `_run_reynolds()` passes GUI values density/velocity/length/viscosity to `compute_reynolds_number()`; exception becomes `GREŠKA: {exc}` in `fluid_result`. Intended GUI defaults: 1000 kg/m³, 2 m/s, 0.05 m, 0.001 Pa·s. Viscosity calls `setValue(0.001)` before `setDecimals(6)`. Engine computes `Re=rho*v*L/mu`, rejects `mu<=0` with `ValueError("Dynamic viscosity must be positive")`. Non-GUI check gives Re=100000 for intended inputs.

Unproven hypothesis: Qt spin-box precision/order may quantize 0.001 to 0.0, causing the engine error.

NEXT: recover exact runtime viscosity value or exact exception text from original Actions job `98404288987`. READ ONLY. No source/PR/GUI/architecture/Python/Actions/limiter/RCI-AD changes until proven.

Genealogy correction: Reynolds run is not `3d0c15d5...`; actual checkout is `bcec0d7...`.

This checkpoint is documentation on `main` only and does not alter Reynolds source.
