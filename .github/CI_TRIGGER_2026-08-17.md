# Controlled CI trigger

Purpose: trigger the canonical `main` Verification Pipeline and Windows Executable workflows after repository consolidation, without changing application or scientific logic.

Date: 2026-08-17

## Consolidation gate

This trigger follows the Quantity import migration and retirement of the obsolete `lat_ces/modules/quantity.py` compatibility bridge. CI must validate the post-retirement state before any further RETIRE action.