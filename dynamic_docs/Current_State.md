<!-- Purpose: A snapshot of where the project stands right now -- what works, what is in progress, what is broken. Rewritten by Claude each session. -->

## Status: In Progress — Session 2 complete

**Codebase:** `code_base/chartgen/` — Session 2 (Workfile rename) is done. `.cgp` → `.cgw` throughout; `ProjectState` → `WorkfileState` (field `cgp_path` → `workfile_path`, `project_name` → `workfile_name`); `m14_project_file`/`project_file.py` → `m14_workfile_file`/`workfile_file.py`; internal archive contents `project_info.json` → `workfile_info.json` and `project_config/` → `workfile_config/`; sidebar/dialog UI text and session-state keys updated to match ("New Workfile", "Open Workfile", `workfile_state`, etc.); settings key `project_folder` → `workfile_folder` (still not populated anywhere in `app.py` — pre-existing gap, not fixed this session, noted in Refactoring Issues Part 2). Genuine TBN-project references were identified and left untouched: `settings["project_name"]`/`settings["project_id"]`, the TBN projects API and its `project_id`/`project_name` fields, and the "Project Details"/"Import Project Data" tab titles — the user confirmed these three should stay as TBN references. The user approved the full code diff before it was applied.

**Documentation:** All seven reference documents remain mirrored in `static_docs_mirror/project_files`, kept in sync mid-session per the Docs Maintenance Guide. Changes this session: Architecture, Functional Spec, Glossary, and Feature List brought into line with the Workfile rename (ground-truth-checked against the updated code, not assumed from the prior session's plan); Refactoring Issues Session 2 marked done in Session 1's style, recording the three TBN-reference decisions, the unpopulated `workfile_folder` gap, and a flag that "project root" (Decision 9's original disambiguation concern) no longer appears anywhere in the current doc or code. A follow-on cleanup pass then removed stale `m10_project_config`/`m11_data_cache` references (module tree entries, table rows, and the now-redundant "M10/M11 status" paragraph) from Architecture and Glossary — both modules were retired in Session 1 but the trees still listed them. Primer was not touched (edit-locked; doesn't use "Project" in the file-lifecycle sense).

**Git:** Repository initialised on `C:\mcp_projects\ChartGen_PreFactor`, remote linked, initial commit and push completed. Session 1 and Session 2's work not yet committed.

## Planned session breakdown (ChartGen_PreFactor scope)

| Session | Focus | Status |
|---|---|---|
| 1 | Quick wins — dead code + doc-only fixes | **Complete** |
| 2 | Workfile rename | **Complete** |
| 3 | Remaining terminology renames | Not started |
| 4 | Population stacking & explicit-value tokens | Not started |
| 5 | PopulationShape redesign | Not started |
| 6 | Concurrency review | Not started |
| 7 | Peer group / reference data | Not started |
| 8 | Placeholder simplification | Not started |
| 9 | Strip module numbering from code_base | Not started |
| 10 | Docstring protocol and review | Not started |

Items passed to the main refactor (not in this project's scope): type coercion at the CSV/WorkfileState boundary, multi-project/multi-database support, `.cgw` file association and installer, Text Engine/Batch Controller module split, modular structure discussion (incl. nested sub-packages such as `chart_engine/tweaks/`, and `m15_insertions`), finding a permanent home for `constants_temp`, and a full content review of `app.py`.
