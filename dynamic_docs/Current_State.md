<!-- Purpose: A snapshot of where the project stands right now -- what works, what is in progress, what is broken. Rewritten by Claude each session. -->

## Status: In Progress — Refactoring Issues Session 4 (Population stacking & explicit-value tokens) complete, including a follow-on peer-group simplification

**Codebase:** `code_base/chartgen/` — population resolution reworked and confirmed working end-to-end, then simplified further on request:

- `build_population_shapes` (`m06_assembly_engine/assembly_engine.py`) implements the **scope-plus-independent-layers** model: the first populations-string token defines the full comparison population; every subsequent token (including `Selected`) resolves independently against that scope, not cumulatively. Explicit-value tokens (`Region(Wales)`) work alongside the existing empty-bracket form (`Region()`), via the same code path. An unresolvable/empty first token returns no population shapes (no fallback substitution) by design; unresolvable subsequent tokens are still silently skipped — no warning mechanism exists anywhere in this function.
- `unit_id` standardised to `str` throughout the codebase (`Unit` and its subclasses in `m04_data_shapes/shapes.py`, `ReportContext` in `m12_local_config/local_config.py`), coerced once at each true ingestion boundary — `api_client.get_submissions()` for the roster, and each `transformers.py` chart-data transform function. The Excel `insert_from_excel` driver-range write is left as a string, per instruction, to observe how Excel handles it.
- **Peer groups are a single mechanism, not two.** There is no binary/flag column type — a simple yes/no group (e.g. Shelford Group) is authored as an ordinary `Name()` column, with a lowercase `x` (or a blank) marking units that don't belong to any group for that column. Both are treated identically: `get_peer_group_value_options` (`local_config.py`) excludes both from discovered peer-group values, and `build_population_shapes`'s empty-bracket resolution treats a unit's own `x` the same as blank (no group, not an error). This was never a working feature being removed — the "binary column" type had been documented as planned but was never implemented in `build_population_shapes`.
- The Running Order populations multi-select (`app.py`, row-edit dialog) is fully generic: `get_peer_group_value_options` discovers every `Name()` peer-group column in `units.csv` and every distinct value within it, with no column name hard-coded anywhere.
- A temporary debug dump (`population_debug.txt`, written from `insert_chart`) was used during testing to diagnose the original zero-count issue and has since been fully removed, along with the debug block itself.

**Documentation:** Four of the six reference documents now reflect the single-mechanism peer-group model — Functional Spec §7.2 (rewritten: one `Name()` mechanism, `x`/blank noted), §10.4 (scope-plus-layers resolution model, rewritten this session), Feature List (`Name()` row: Partial → Complete, "Binary peer group columns" row removed entirely), Glossary (Peer group entry rewritten to describe one mechanism; "numeric" dropped from the Unit ID entry as a separate small correction), and Refactoring Issues (Session 4 marked done including the `unit_id` root-cause finding and the later peer-group-simplification follow-on note; Session 7's now-obsolete "binary peer group review logic" item removed outright, since it described something never built and no longer wanted). Architecture and Primer were confirmed unaffected and left untouched. All written to the mirror.

**Git:** Repository on `C:\mcp_projects\ChartGen_PreFactor`. This session's work is committed as part of this close-down.

## Planned session breakdown (ChartGen_PreFactor scope)

| Session | Focus | Status |
|---|---|---|
| 1 | Quick wins — dead code + doc-only fixes | **Complete** |
| 2 | Workfile rename | **Complete** |
| 3 | Remaining terminology renames | **Complete** |
| 4 | Population stacking & explicit-value tokens | **Complete** |
| 5 | PopulationShape redesign | Not started |
| 6 | Concurrency review | Not started |
| 7 | Peer group / reference data | Not started — scope now narrower: only `organisations.csv` storage remains; binary peer group review logic was removed as a non-issue (see Session 4). |
| 8 | Placeholder simplification | Not started |
| 9 | Strip module numbering from code_base | Not started |
| 10 | Docstring protocol and review | **Complete** (resequenced ahead of Session 3) |

Items passed to the main refactor (not in this project's scope): type coercion at the CSV/WorkfileState boundary (now two known instances — `enabled` and `unit_id` — plus `organisation_id` flagged as a further unaddressed one), whether untyped dict/row contracts should become typed structures, multi-project/multi-database support, `.cgw` file association and installer, Text Engine/Batch Controller module split, modular structure discussion (incl. nested sub-packages such as `chart_engine/tweaks/`, and `m15_insertions`), finding a permanent home for `constants_temp`, and a full content review of `app.py`.
