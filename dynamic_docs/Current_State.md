<!-- Purpose: A snapshot of where the project stands right now -- what works, what is in progress, what is broken. Rewritten by Claude each session. -->

## Status: In Progress — Refactoring Issues Session 3 (Remaining terminology renames) complete

**Codebase:** `code_base/chartgen/` — all five Session 3 terminology items executed:
- `ComparativeUnit` (and its use in docstrings/UI as "comparative unit"/"comparative population") renamed to plain **Unit**/**Population** throughout `m04_data_shapes/shapes.py` and elsewhere. The stray "comparator population" string in the `app.py` Populations caption corrected.
- "Item table" renamed to **Population table** (the `app.py` expander label is now "Units — population table").
- "Submission" / `submission_id` / `submission_code` renamed to Unit-based terminology, with a deliberate boundary: `api_client.py`'s `get_submissions()` and the raw API JSON keys (`submissionId`, `submissionCode`, `submissionName`) are untouched — that's the external contract. Everything from the point of ingestion onward uses `unit_id`/`unit_code`/`unit_name`: `WorkfileState.units` (was `.submissions`), `units.csv` (was `submissions.csv`), `ReportContext`, the `Unit` data-shape fields, settings key `selected_unit_id` (was `selected_submission_id`). Fields describing the submission event itself rather than unit identity (`submission_year`, `submission_level`, `submission_service_count`) were left unrenamed. Downstream wording also updated for consistency ("Multiple units from same org", "Multi-unit table expansion").
- "Flag token" renamed to **Text Tag** throughout code and documentation.
- "Batch" terminology resolved as a split: the Streamlit tab renamed from "Batches"/"Batch Processing" to **Outputs** (short) / **Create Outputs** (long); `Run Selected`/`Run Batch`/`Run All` and the internal batch-processing concept are unchanged, since "batch" is the correct word for the machine-level loop and "Run Batch" is the one place a human genuinely means "more than one, less than all."

**Documentation:** All five of the six reference documents that could be affected were updated with targeted edits (not rewrites), per the Docs Maintenance Guide's routing table: Glossary, Functional Spec, Architecture, Feature List, and Refactoring Issues (Session 3 marked done, in the same strikethrough style as Sessions 1/2/10; Part 2's stale references to `SUBMISSIONS_FIELDNAMES`/`ComparativeUnit`/`_submission_label` updated to the new names). Primer and the Docs Maintenance Guide were not touched. All written to the mirror.

**Git:** Repository on `C:\mcp_projects\ChartGen_PreFactor`. This session's work (Progression_Log Session 5) is committed as part of this close-down.

## Planned session breakdown (ChartGen_PreFactor scope)

| Session | Focus | Status |
|---|---|---|
| 1 | Quick wins — dead code + doc-only fixes | **Complete** |
| 2 | Workfile rename | **Complete** |
| 3 | Remaining terminology renames | **Complete** |
| 4 | Population stacking & explicit-value tokens | Not started |
| 5 | PopulationShape redesign | Not started |
| 6 | Concurrency review | Not started |
| 7 | Peer group / reference data | Not started |
| 8 | Placeholder simplification | Not started |
| 9 | Strip module numbering from code_base | Not started |
| 10 | Docstring protocol and review | **Complete** (resequenced ahead of Session 3) |

Items passed to the main refactor (not in this project's scope): type coercion at the CSV/WorkfileState boundary, whether untyped dict/row contracts should become typed structures, multi-project/multi-database support, `.cgw` file association and installer, Text Engine/Batch Controller module split, modular structure discussion (incl. nested sub-packages such as `chart_engine/tweaks/`, and `m15_insertions`), finding a permanent home for `constants_temp`, and a full content review of `app.py`.
