<!-- Purpose: A snapshot of where the project stands right now -- what works, what is in progress, what is broken. Rewritten by Claude each session. -->

## Status: In Progress — Refactoring Issues Session 4 (Population stacking & explicit-value tokens) complete

**Codebase:** `code_base/chartgen/` — population resolution reworked and confirmed working end-to-end:
- `build_population_shapes` (`m06_assembly_engine/assembly_engine.py`) rewritten to the **scope-plus-independent-layers** model: the first populations-string token defines the full comparison population; every subsequent token (including `Selected`) resolves independently against that scope, not cumulatively. Explicit-value tokens (`Region(Wales)`) are now implemented alongside the existing empty-bracket form (`Region()`), via the same code path. Net shorter than the prior sequential-intersection version. An unresolvable/empty first token returns no population shapes (no fallback substitution) by design; unresolvable subsequent tokens are still silently skipped — no warning mechanism was added.
- `unit_id` standardised to `str` throughout the codebase (`Unit` and its subclasses in `m04_data_shapes/shapes.py`, `ReportContext` in `m12_local_config/local_config.py`), coerced once at each true ingestion boundary — `api_client.get_submissions()` for the roster, and each `transformers.py` chart-data transform function — rather than left as `int` or coerced defensively at points of use. This fixed a pre-existing (not newly introduced) boundary bug that was the actual cause of population resolution testing zero units. The Excel `insert_from_excel` driver-range write is left as a string, per instruction, to observe how Excel handles it.
- The Running Order populations multi-select (`app.py`, row-edit dialog) is now fully generic: `get_peer_group_value_options` (`local_config.py`) discovers every `Name()` peer-group column in `units.csv` and every distinct value within it, with no column name hard-coded anywhere.
- A temporary debug dump (`population_debug.txt`, written from `insert_chart`) was used during testing to diagnose the above and has since been fully removed, along with the debug block itself.

**Documentation:** Three of the six reference documents updated, per the Docs Maintenance Guide's routing table — Functional Spec §10.4 (resolution model, worked example, and token-support caveat rewritten to match), Feature List (`Name()` peer group row: Partial → Complete), and Refactoring Issues (Session 4 marked done, including the `unit_id` root-cause finding; Part 2's type-coercion item extended to flag `organisation_id` as an unaddressed instance of the same latent int/str inconsistency). Architecture, Glossary, and Primer were confirmed unaffected and left untouched. All written to the mirror.

**Git:** Repository on `C:\mcp_projects\ChartGen_PreFactor`. This session's work (Progression_Log Session 6) is committed as part of this close-down.

## Planned session breakdown (ChartGen_PreFactor scope)

| Session | Focus | Status |
|---|---|---|
| 1 | Quick wins — dead code + doc-only fixes | **Complete** |
| 2 | Workfile rename | **Complete** |
| 3 | Remaining terminology renames | **Complete** |
| 4 | Population stacking & explicit-value tokens | **Complete** |
| 5 | PopulationShape redesign | Not started |
| 6 | Concurrency review | Not started |
| 7 | Peer group / reference data | Not started |
| 8 | Placeholder simplification | Not started |
| 9 | Strip module numbering from code_base | Not started |
| 10 | Docstring protocol and review | **Complete** (resequenced ahead of Session 3) |

Items passed to the main refactor (not in this project's scope): type coercion at the CSV/WorkfileState boundary (now two known instances — `enabled` and `unit_id` — plus `organisation_id` flagged as a further unaddressed one), whether untyped dict/row contracts should become typed structures, multi-project/multi-database support, `.cgw` file association and installer, Text Engine/Batch Controller module split, modular structure discussion (incl. nested sub-packages such as `chart_engine/tweaks/`, and `m15_insertions`), finding a permanent home for `constants_temp`, and a full content review of `app.py`.
