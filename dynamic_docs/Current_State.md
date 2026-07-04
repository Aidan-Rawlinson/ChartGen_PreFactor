<!-- Purpose: A snapshot of where the project stands right now -- what works, what is in progress, what is broken. Rewritten by Claude each session. -->

## Status: In Progress — Pre-refactor planning complete, Session 1 not yet started

**Codebase:** `code_base/chartgen/` contains the vibe-coded proof-of-concept, structured per the Architecture doc's module map (`app.py`, `run_chartgen.bat`, `requirements.txt`, `.streamlit/`, `user_resources/`, 12 numbered modules under `modules/`, plus `Claude_Please_Check.md` at the app root, flagged for deletion). No code has been modified yet — structure reviewed only, contents not read.

**Documentation:** Six reference documents (Primer, Architecture, Functional Spec, Feature List, Glossary, Refactoring Issues) plus the Docs Maintenance Guide are in place and mirrored in `static_docs_mirror/project_files`. `Refactoring_issues_known.md` was restructured this session into a two-part document: Part 1 (this project, grouped into 9 planned sessions) and Part 2 (passed to the main refactor) — written to the mirror. Mirror confirmed to match Project Files for all seven documents at review, and the Docs Maintenance Guide's Section 8 (Mid-Session Writes) was confirmed already present.

**Git:** Repository initialised on `C:\mcp_projects\ChartGen_PreFactor`, remote linked, initial commit and push completed.

## Planned session breakdown (ChartGen_PreFactor scope)

| Session | Focus | Status |
|---|---|---|
| 1 | Quick wins — dead code + doc-only fixes | Not started |
| 2 | Workfile rename | Not started |
| 3 | Remaining terminology renames | Not started |
| 4 | Population stacking & explicit-value tokens | Not started |
| 5 | PopulationShape redesign | Not started |
| 6 | Concurrency review | Not started |
| 7 | Peer group / reference data | Not started |
| 8 | Placeholder simplification | Not started |
| 9 | Strip module numbering from code_base | Not started |

Items passed to the main refactor (not in this project's scope): type coercion at the CSV/ProjectState boundary, multi-project/multi-database support, `.cgp` file association and installer, Text Engine/Batch Controller module split, modular structure discussion (incl. `m15_insertions`).
