<!-- Purpose: A snapshot of where the project stands right now -- what works, what is in progress, what is broken. Rewritten by Claude each session. -->

## Status: Refactoring Issues Sessions 6, 7, and 8 complete — code and documentation, fully committed

**Session 6 (Concurrency review)** — confirmed complete and committed this session. Its documentation had been deferred at the prior close-down pending message-wording confirmation; verified via `environment/git_log.txt` (push completed 2026-07-08 09:42:54) that the doc write-up had since been committed and pushed. Mirror content checked against Project Files and confirmed matching. No outstanding action remained.

**Session 7 (Peer group / reference data)** — `organisations.csv` storage removed entirely, not reconsidered. It served no purpose beyond the point of creation: organisation data is fetched once at New Workfile creation and used immediately, in memory, to resolve `Region()` onto `units.csv`; nothing else ever read the persisted copy. Removed: `WorkfileState.organisations`, its load in `open_workfile`, its write in `save_workfile`, `organisations.csv` from `_write_empty_cgw`, `ORGANISATIONS_FIELDNAMES` from `constants_temp.py`, and the corresponding assignment in `app.py`'s New Workfile flow. The API fetch and one-time in-memory lookup are unchanged. Pre-existing `.cgw` files retain a stale `organisations.csv`; this is deliberately left alone — no detection/cleanup code was added, since that would mean writing code whose only purpose is to acknowledge something that shouldn't exist.

Documentation for this removal was handled on the principle that the store's non-existence, not its removal, is the fact to document: Architecture and Feature List had all `organisations.csv`/`WorkfileState.organisations` references deleted outright (file tree, table rows, in-memory diagram, CSV-format note) rather than marked as changed. Functional Spec, Glossary, and Primer were checked and confirmed never to have described the store as such — no edits needed there. Refactoring Issues' Session 7 entry was marked done with the removal recorded, since that document's job is specifically to track what happened.

**Session 8 (Placeholder simplification)** — `_is_chart_placeholder` (`template_reader.py`) revised in two ways. The placeholder-type whitelist widened from 4 to 8 native PowerPoint placeholder types (`OBJECT`, `PICTURE`, `CHART`, `BITMAP`, plus newly added `TABLE`, `ORG_CHART`, `MEDIA_CLIP`, `BODY`) — covering every content-bearing type a designer could plausibly insert (Content, Picture, Chart, Clip Art, Table, SmartArt, Media, Text), while deliberately excluding role-specific text placeholders (Title, Subtitle, Date, Footer, Header, Slide Number, and vertical variants) that a human would never repurpose as a content slot. The name-based classification bypass (`shape.name.lower().startswith("chart")`) was removed entirely — a placeholder is now recognised purely by its native PowerPoint type, never by name. Previously, a placeholder of an unlisted type could only be picked up by naming it "Chart…"; an unlisted, unnamed placeholder failed silently with no warning. The widened whitelist removes the need for that escape hatch. Confirmed via `running_order.py` that placeholder names are used only for Running Order row labelling, never classification, so nothing downstream was affected.

Documentation updated: Functional Spec §6.2 (heading and text — recognition is now by type, not name; the 8 types listed; no naming convention required) and §6.1 (dropped "named" from its lead sentence). Glossary's Placeholder entry rewritten to match. Architecture, Feature List, and Primer confirmed unaffected. Refactoring Issues' Session 8 entry marked done.

All documentation changes for both sessions were written to the mirror during the session, per Docs Maintenance Guide §8.

**Git:** Not yet committed this session — code and documentation changes for Sessions 7 and 8 are pending the close-down commit.

## Planned session breakdown (ChartGen_PreFactor scope)

| Session | Focus | Status |
|---|---|---|
| 1 | Quick wins — dead code + doc-only fixes | **Complete** |
| 2 | Workfile rename | **Complete** |
| 3 | Remaining terminology renames | **Complete** |
| 4 | Population stacking & explicit-value tokens | **Complete** |
| 5 | PopulationShape redesign | **Complete** |
| 6 | Concurrency review | **Complete** |
| 7 | Peer group / reference data | **Complete** |
| 8 | Placeholder simplification | **Complete** |
| 9 | Strip module numbering from code_base | Not started — next up |
| 10 | Docstring protocol and review | **Complete** (resequenced ahead of Session 3) |

Only Session 9 remains before Part 1 of the Refactoring Issues log is fully worked through.

Items passed to the main refactor (not in this project's scope): type coercion at the CSV/WorkfileState boundary (two known instances — `enabled` and `unit_id` — plus `organisation_id` flagged as a further unaddressed one), whether untyped dict/row contracts should become typed structures, multi-project/multi-database support, `.cgw` file association and installer, Text Engine/Batch Controller module split, modular structure discussion (incl. nested sub-packages such as `chart_engine/tweaks/`, and `m15_insertions`), finding a permanent home for `constants_temp`, a full content review of `app.py`, the deferred `beforeunload` browser warning and unpursued autosave options from Session 6, and the two lock gaps noted in Session 6 (no re-check at Save; `locked_by` overwritten by "Open anyway"). `base_charts.py`'s dead `_layer_colour` function and its lack of any other tweak/architecture work remain out of scope until a dedicated session.
