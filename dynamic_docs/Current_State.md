<!-- Purpose: A snapshot of where the project stands right now -- what works, what is in progress, what is broken. Rewritten by Claude each session. -->

## Status: In Progress — Refactoring Issues Session 5 (PopulationShape redesign) complete

**Codebase:** `code_base/chartgen/` — `PopulationShape` wrapper retired:

- `population_label: Optional[str] = None` added directly to the three canonical data shapes (`NumericSeries`, `NumericCompositional`, `CategoricalCompositional`) in `m04_data_shapes/shapes.py`. The `PopulationShape` dataclass (`role`/`label`/`shape`) is removed.
- `build_population_shapes` (`m06_assembly_engine/assembly_engine.py`) now returns the filtered data shapes directly, with `population_label` set via `dataclasses.replace` instead of wrapping each in `PopulationShape`. `insert_chart`'s no-populations-resolved fallback updated to match.
- `role` was dropped rather than kept as `population_role` — it carried no information `label` didn't already have (identical to `label` for `All`/`Selected`; just the raw token text for peer-group tokens). Only `population_label` survives.
- `base_charts.py` (all 17 Base Chart functions) and `app.py`'s Chart Preview fallback updated mechanically to match: every `ps.shape` → `ps`, every `ps.role`/`ps.label` → `ps.population_label`. No other logic in `base_charts.py` was touched — it remains flagged as due for a proper rewrite, not this session's scope.
- Noted in passing, not fixed: `_layer_colour` in `base_charts.py` is defined but never called anywhere in the file — dead code pre-dating this session.

**Documentation:** Architecture §5 (in-memory structure diagram and table), Functional Spec §10.4 (chart data flow) and §8.1 (immutability note), Glossary Cluster 7 (`Population shape` entry renamed to `Population label`), and Refactoring Issues (Session 5 marked done) all updated to describe `population_label` on the data shape itself rather than a `PopulationShape` wrapper. Feature List and Primer confirmed unaffected. All written to the mirror and verified against the re-uploaded Project Files.

**Git:** Repository on `C:\mcp_projects\ChartGen_PreFactor`. This session's work is committed as part of this close-down.

## Planned session breakdown (ChartGen_PreFactor scope)

| Session | Focus | Status |
|---|---|---|
| 1 | Quick wins — dead code + doc-only fixes | **Complete** |
| 2 | Workfile rename | **Complete** |
| 3 | Remaining terminology renames | **Complete** |
| 4 | Population stacking & explicit-value tokens | **Complete** |
| 5 | PopulationShape redesign | **Complete** |
| 6 | Concurrency review | Not started |
| 7 | Peer group / reference data | Not started — scope now narrower: only `organisations.csv` storage remains; binary peer group review logic was removed as a non-issue (see Session 4). |
| 8 | Placeholder simplification | Not started |
| 9 | Strip module numbering from code_base | Not started |
| 10 | Docstring protocol and review | **Complete** (resequenced ahead of Session 3) |

Items passed to the main refactor (not in this project's scope): type coercion at the CSV/WorkfileState boundary (two known instances — `enabled` and `unit_id` — plus `organisation_id` flagged as a further unaddressed one), whether untyped dict/row contracts should become typed structures, multi-project/multi-database support, `.cgw` file association and installer, Text Engine/Batch Controller module split, modular structure discussion (incl. nested sub-packages such as `chart_engine/tweaks/`, and `m15_insertions`), finding a permanent home for `constants_temp`, and a full content review of `app.py`. `base_charts.py`'s dead `_layer_colour` function and its lack of any other tweak/architecture work remain out of scope until a dedicated session.
