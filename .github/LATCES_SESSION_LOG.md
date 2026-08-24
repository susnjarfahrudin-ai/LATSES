# LAT-CES Persistent Session Log

## Purpose

Persistent project hand-off and recovery log for LATSES work sessions. This file is the canonical session checkpoint document for continuing work after chat limits, new chats, or interrupted sessions.

## Operating rule

Do not rely on chat memory as the sole source of project state. At every significant technical checkpoint, record the evidence and the exact next action here.

### Checkpoint fields

- **DATETIME:** ISO-8601 timestamp with timezone when known
- **SESSION:** short session identifier
- **ACTION:** what was inspected or changed
- **EVIDENCE:** commit SHA / PR / Actions Run / file path / artifact
- **BRANCH:** branch or ref
- **RESULT:** factual result
- **DECISION:** accepted/rejected/unknown
- **OPEN:** unresolved items
- **NEXT:** exact next technical step
- **LINKS:** GitHub navigation links

## Safety rules

1. Read-only recovery work must not modify application code.
2. Do not merge, restore, or rebuild historical code unless explicitly authorized.
3. Never declare something lost merely because it is absent from `main`; check branches, commits, PRs and workflow history first.
4. Distinguish verified facts from hypotheses.
5. Before starting a new recovery operation, read this file first and continue from the latest checkpoint.
6. When a session is approaching a context limit, write a final checkpoint containing the exact stopping point and next action.

## Canonical restart command

> **OTVORI `.github/LATCES_SESSION_LOG.md` NA `main` I NASTAVI OD ZADNJEG CHECKPOINTA. PRVO PROVJERI STANJE NA GITHUBU, NE PONAVLJAJ VEĆ ZAVRŠENE KORAKE, NE DIRAJ KOD BEZ MOG ODOBRENJA.**

## Initial checkpoint — 2026-08-21

- **ACTION:** Established persistent GitHub session-log mechanism.
- **EVIDENCE:** Repository `susnjarfahrudin-ai/LATSES`.
- **BRANCH:** recovery branch created from `main` for this log.
- **RESULT:** Direct write to protected `main` was rejected; therefore the log is being introduced through a recovery branch and pull request.
- **DECISION:** Keep `main` untouched until the PR is reviewed/merged.
- **OPEN:** PR creation and merge status.
- **NEXT:** Review this file in the PR, then merge only this documentation change if authorized.

## Project recovery context to preserve

Current recovery investigation concerns the canonical location and history of:

- Scientific Model / SMC-001 → SMC-004
- SCI 1–145
- modules 0001–0055
- Building Model
- Dimension systems and duplicate Dimension architecture
- `gui_master.py`
- `gui_complete.py`
- `MasterBuildingWorkspaceApp`
- `CompleteBuildingWorkspaceApp`
- `complete_tabs` / `tabs`
- CLI
- `pyproject.toml`
- PyInstaller and `.spec` files
- Windows Installer
- Verification workflow
- Installer workflow
- Actions runs and artifacts

Important historical checkpoints already identified in the investigation include `abd49fa`, `86aa38f`, `f7e0ddc`, `170ec750`, and the later GUI/Installer recovery trail around `f132f28f`. These are evidence points, not assumptions that code should be restored.

## Evidence-first workflow

For every future investigation:

`checkpoint → GitHub evidence → file/tree/diff → conclusion → next checkpoint`

At the end of each meaningful operation, append a new dated checkpoint to this document rather than relying on conversational context alone.
