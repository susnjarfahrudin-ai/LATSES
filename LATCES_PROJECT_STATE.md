# LAT-CES Project State — Reynolds GUI forensic checkpoint

**READ-ONLY investigation state; no Reynolds source-code fix.**

Exact failing run: `Fahro Terenska Aplikacija - Installer` #17, run `33037789303`, job `98404288987`, branch `fahro-terenska-aplikacija`, checkout `bcec0d7fb36d012b8379b2796b83d7239c3b7d64`, parent `7005e4c129f11a6199016d0a5bfe45d50c93dd28`.

Verified: checkout/CPython 3.10.11/dependencies succeeded; first failure was `verify_all()` → `verify_gui_domain_access()` at `assert reynolds_result and "GREŠKA:" not in reynolds_result`.

At exact commit, `_run_reynolds()` reads density/velocity/length/viscosity widget values and writes `GREŠKA: {exc}` on exception. GUI intended defaults: 1000 kg/m³, 2 m/s, 0.05 m, 0.001 Pa·s. Viscosity widget calls `setValue(0.001)` before `setDecimals(6)`. Engine computes `Re=rho*v*L/mu` and rejects `mu<=0` with `ValueError("Dynamic viscosity must be positive")`. Non-GUI suite verifies 100000 for intended inputs.

**Unproven hypothesis:** Qt spin-box precision/order may quantize 0.001 to 0.0, causing the engine error.

**Next proof step, READ ONLY:** recover the exact runtime viscosity value or exact exception text from original Actions job `98404288987`. No source/PR/GUI/architecture/Python/Actions/limiter/RCI-AD changes until proven.

Genealogy correction: Reynolds run is not `3d0c15d5...`; actual run checkout is `bcec0d7...`.

This document is a continuity checkpoint on `main` only and does not alter the Reynolds source branch.
