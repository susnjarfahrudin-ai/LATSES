# LAT-CES Session Recovery Protocol

This file defines how an engineering session resumes without reconstructing the project from conversation history.

## Start-of-session order

1. Read `.github/LATCES_PROJECT_STATE.json`.
2. Read `.github/LATCES_PROJECT_STATE.md` for human-readable history.
3. Inspect the active PR listed in the JSON.
4. Inspect the latest commit and its Verification + Windows Installer workflow runs.
5. Continue from `current_blocker` and `next_actions`.

## End-of-session order

After every meaningful change, update the checkpoint with:

- active branch;
- active PR;
- latest commit;
- CI run numbers and status;
- completed work;
- current blocker;
- exact next action;
- decisions that must not be reopened.

## Release evidence rule

A LAT-CES Windows build is not release-ready merely because CI imports the GUI or the executable starts. For the master GUI, the validation path must exercise the user-facing command callbacks, including Reference House, Tlocrt, Presjek, 3D, Provjera and Izvještaj.

## Failure workflow

When any Verification, EXE, Installer, smoke test or packaged-GUI step fails:

1. Freeze the exact failing source SHA.
2. Record the exact workflow run, job, step and failure/log evidence.
3. Classify the failure as source, dependency, integration, runtime, packaging or infrastructure.
4. Locate the smallest concrete source/function/dependency cause.
5. Apply the smallest targeted repair; do not restart the project or reopen settled architectural decisions.
6. Add or update a regression test that reproduces the failure where practical.
7. Run the narrow verification that proves the repair.
8. Re-run the full Verification + EXE + Installer evidence chain on the repaired SHA.
9. Compare the repaired result with the frozen failing SHA and record the outcome in the project state.
10. Do not accept a release candidate until the actual packaged GUI and installer have been exercised.

## Module Extension / Long-Term Stability Workflow

All new capabilities must extend the platform around the canonical `BuildingModel`, which remains the single source of truth.

For every new module or feature, use this contract:

`INPUT -> canonical BuildingModel`

`ENGINE -> module-owned domain logic/formulas`

`OUTPUT -> structured engineering result`

`VALIDATION -> module tests + integration test`

`GUI -> input/presentation only; no ownership of engineering formulas`

`REPORT -> result + provenance`

`PACKAGING -> module survives EXE/Installer build and packaged smoke validation`

Module rules:

- Do not create a second authoritative model of the same building data.
- Do not create hidden engineering assumptions inside GUI or catalog presentation code.
- Prefer stable interfaces between modules over direct chains of module-to-module dependencies.
- Missing engineering inputs must remain explicit `INPUT_REQUIRED` / `CHECK` states rather than invented values.
- New modules must preserve existing canonical behavior and regression coverage.
- New domain capability is accepted only after its source tests, integration path and packaged runtime path are validated.
- The extension workflow is additive: new modules should attach to the canonical model without destabilizing unrelated domains.

This is the required long-term expansion pattern for LAT-CES.

## Anti-loop rule

Before opening a new bug-fix branch, compare the failure with the historical decisions and closed PRs recorded in the checkpoint. Reuse the active workstream when the problem was already analysed and has a reproducible existing solution.

## Communicator/GitHub integration

The repository itself does not provide ChatGPT with permanent hidden memory. The persistent hand-off is therefore stored in GitHub. A future session can fetch these files through the GitHub connector and use them as the authoritative project navigation point.
