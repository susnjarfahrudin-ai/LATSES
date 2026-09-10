# LAT-CES Project State — Reynolds GUI forensic checkpoint

## Status
READ-ONLY forensic investigation. No source-code fix. Documentation checkpoint only.

### Exact Reynolds run
- Workflow: `Fahro Terenska Aplikacija - Installer`
- Run #17 / ID `33037789303`
- Job `build-field-app-installer` / ID `98404288987`
- Branch `fahro-terenska-aplikacija`
- Checkout HEAD `bcec0d7fb36d012b8379b2796b83d7239c3b7d64`
- Commit: `test(terenska): validate Reynolds GUI result semantics`
- Parent `7005e4c129f11a6199016d0a5bfe45d50c93dd28`

### Verified CI facts
- Checkout succeeded.
- CPython 3.10.11 setup succeeded.
- Dependencies installed successfully.
- Failure occurred in `Compile and verify field application`, in `verify_all()` → `verify_gui_domain_access()`.
- First concrete assertion failure: `assert reynolds_result and "GREŠKA:" not in reynolds_result`.
- Packaging/installer steps were skipped.

### Exact GUI path at `bcec0d7`
`_run_reynolds()` passes four widget values to `compute_reynolds_number`: density, velocity, characteristic length, dynamic viscosity. Exceptions are written to `fluid_result` as `GREŠKA: {exc}`. The verification rejects empty/error output, parses the numeric result after `:`, and requires it to be > 0.

### Source defaults at `bcec0d7`
- density 1000.0 kg/m³
- velocity 2.0 m/s
- characteristic length 0.05 m
- intended dynamic viscosity 0.001 Pa·s

The viscosity widget calls `setValue(0.001)` before `setDecimals(6)`.

### Engine
`Re = density * velocity * characteristic_length / dynamic_viscosity`.
The engine raises `ValueError("Dynamic viscosity must be positive")` for viscosity <= 0.
The same file's non-GUI verification asserts `Re(1000, 2, 0.05, 0.001) == 100000.0`.

### Strong but unproven hypothesis
The `QDoubleSpinBox` precision/order may quantize `0.001` before `setDecimals(6)`, causing `.value()` to become 0.0. That would produce `GREŠKA: Dynamic viscosity must be positive` and exactly explain the CI assertion.

This is **NOT yet final proof**.

## Next proof step — READ ONLY
Determine either:
1. the actual runtime `self.fluid_viscosity.value()` on exact commit `bcec0d7`, or
2. the exact exception text produced by `_run_reynolds()` in the original CI log.

Do not modify source, PRs, architecture, Python version, Actions, limiter, RCI-AD, or GUI during this proof step.

## Genealogy correction
The Reynolds run is **not** commit `3d0c15d5aa5b088fddedd8056be724a2187f3fa1`; that line diverged. The real Reynolds run checked out `bcec0d7fb36d012b8379b2796b83d7239c3b7d64`.

## Checkpoint commits
This documentation checkpoint was recorded on `main` only so the forensic state survives a chat transition. It does not alter the Reynolds source branch.
