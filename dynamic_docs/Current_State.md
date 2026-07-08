<!-- Purpose: A snapshot of where the project stands right now -- what works, what is in progress, what is broken. Rewritten by Claude each session. -->

## Status: Refactoring Issues Session 9 complete — module numbering stripped from code_base. Part 1 fully worked through.

Renamed all module folders under `modules/` to drop the `mNN_` prefix (e.g. `m01_data_acquisition` → `data_acquisition`). Full blast-radius scan performed first (34 cross-module references across `app.py` and 9 module files, including two string-built paths to `static_config/chart_type_map.csv`) — all updated to match. One cosmetic "from M02" comment in `running_order.py` also corrected. Old `mNN_` folders and stale `__pycache__` deleted.

Documentation side done per user instruction to keep it simple (search-replace only): Architecture.md and Glossary.md module trees/tables updated to the new names — the only two reference docs containing `mNN_` references. Functional Spec, Feature List, and Primer had none. Refactoring Issues intentionally left with original `mNN_` names, since it's a historical log, not current-state documentation.

## Planned session breakdown (ChartGen_PreFactor scope)

| Session | Focus | Status |
|---|---|---|
| 1–8, 10 | (see prior entries) | **Complete** |
| 9 | Strip module numbering from code_base | **Complete** |

All of Part 1 (Refactoring Issues sessions run within this project) is now complete. Remaining work is Part 2 items, deferred to the main refactor — see `Refactoring_issues_known.md`.

**Git:** Not yet committed this session — close-down commit pending (this session).
