# ChartGen — Refactoring Issues (Known)

This document is split into two parts: items being handled in the ChartGen_PreFactor project (grouped into focused sessions), and items being passed forward to the main refactor.

---

## Part 1 — This Project (ChartGen_PreFactor)

### Session 1 — Quick wins (dead code + doc-only fixes)

* Module numbering incorrect
* Legacy disk-fallback code in M10/M11 — candidate for removal once confirmed nothing in the refactor still depends on it.
* Debug tab (Debug Trace) — never used in practice. Review and likely drop.
* Delete `Claude_Please_Check.md` from the repository — references superseded document names (`Draft_Prototype_Functional_Spec.md` etc.) and no longer reflects the current document set.
* Refer to modules by name, not number, throughout documentation — module numbers are not maintainable over time.
* Stale module docstring in `m03_running_order/running_order.py` — documents the old 12-column schema and an outdated function list; bring in line with the `COLUMNS` and `ALL_FUNCTIONS` constants (or derive the docstring content from them).

### Session 2 — Workfile rename

* Terminology — "Project" collides with TBN's own usage (a benchmarking exercise/data source). Rename the ChartGen-file-lifecycle concept to "Workfile" throughout code and documentation. Priority: do this at the very start of the refactor, since later stages and their documentation will build on the new name. Scope spans:
  - The architectural concept itself — the "Project domain" (Architecture §2, §4, §5) becomes the "Workfile domain".
  - The in-memory object — `ProjectState` becomes `WorkfileState`.
  - File/folder naming in the actual codebase and archive — `.cgp` extension, `m10_project_config`, `m14_project_file`, `project_file.py`, `project_info.json`, the internal `project_config/` folder.
  - Generic prose usage — "opening a project", "project data", "dirty project", "no-project-loaded state", etc. Also note "project root" (Decision 9) is a third, unrelated sense (the software installation folder) worth disambiguating at the same time.
  - UI/tab naming and the mixed cases — "New Project flow" becomes "New Workfile flow" (the flow both selects a TBN project and creates a new ChartGen workfile — the name needs to keep both meanings distinct); tab titles ("Project Setup → Project Details", "Import Project Data"); Feature List group headings and rows ("Project setup & selection", "Project / file structure", "Project file format", "Multi-project application model", etc.).
  - Out of scope — genuine TBN usage of "project" (a benchmarking exercise/data source, `project_id`, "Project Summary Report", "Project Outputs") stays unchanged.
  - Once the code rename lands, the five reference documents (Architecture, Functional Spec, Glossary, Feature List, this issues log) need a full pass to match.

### Session 3 — Remaining terminology renames

* "Comparative unit" / "comparative population" → "Unit" / "Population" — Documentation settles on plain "Unit" and "Population" as the standard terms (per the Primer), with "Reporting Unit" retained as a named special case of Unit. Codebase currently uses the compound form throughout: the `ComparativeUnit` class (`m04_data_shapes/shapes.py`) and its subclasses, "comparative population" in docstrings, and a stray "comparator population" string in the `app.py` UI caption. All require updating to match — class rename, docstring updates, and the one leftover UI string, which was already inconsistent with the Primer's own stated convention before this decision.
* "Item table" terminology — "item" is an early, superseded name for what is now called "Unit"/"Reporting unit". Appears in `m10_project_config/submissions.py` (docstring), and in `app.py` (a UI caption and an expander label, "Submissions — item table"). Rename throughout code and documentation to **Population table** — decided in preference to "Unit table," since "Population" is the stronger human-facing term and "Unit" reads as weak outside the codebase.
* "Submission" / `submission_id` / `submission_code` terminology — should be renamed to Unit-based terminology throughout ("submission" fits as a description, since a Trust submits data, but Unit is the standardised term going forward). Also note: the current Glossary entry's description of Submission as "a single reporting unit's data record" is not accurate as stated — needs correcting as part of this same pass, not just renamed.
* "Flag token" terminology — the term is disliked; review for a clearer alternative. Used for template placeholder strings (e.g. `[selected-reporting-unit-name]`) replaced per-unit by `update_text`, distinct from the Running Order's Enabled column. Replacement term to be agreed before executing the rename.
* "Batch" terminology — Run Selected (a single reporting unit), Run Batch (a subset), and Run All (the full population) are all currently grouped under "Batch Processing," but "batch" conventionally implies more than one. Review and either accept the current usage or find clearer terminology, consistent across the tab name, code, and documentation. Replacement term to be agreed before executing the rename.

### Session 4 — Population stacking & explicit-value tokens

* Population stacking — confirm the correct logical structure for how "Selected" binds in a populations string. Given `Region(Wales)^Hospital_Size(Large)^Selected`, does Selected bind to the full preceding intersection (Region(Wales) AND Hospital_Size(Large)), or only to part of it? The Functional Spec currently documents the former; re-derive and confirm before relying on it. Start the re-derivation from the filter-vs-layer framing now in Functional Spec 10.4 — how Selected binds is a question of how those two patterns compose.
* Explicit-value peer group tokens (`Name(Value)`, e.g. `Region(Wales)`) are not implemented — resolution only handles empty-bracket tokens (`Name()`, the selected unit's own group). Unresolvable tokens are silently dropped rather than warned. Address both in the populations rework, alongside the population stacking item. Depends on the population stacking derivation above.

### Session 5 — PopulationShape redesign

* `PopulationShape` redesign — currently a separate wrapper type (`role`, `label`, `shape` fields) produced by `build_population_shapes`. Proposal: retire the wrapper and add `population_role`/`population_label` as native fields directly on `data_shape` instead — a data shape always represents some population; this should be a normal property of any instance, not a distinct filtered variant. Not yet implemented — current code still uses `PopulationShape` as described in the Architecture and Functional Spec documents.

### Session 6 — Concurrency review

* Review and tighten the concurrency process.

### Session 7 — Peer group / reference data

* Storing `organisations.csv` — flagged as disliked; reconsider this approach.
* Binary peer group review logic.

### Session 8 — Placeholder simplification

* Review placeholder logic — simplify and document the nature of PowerPoint placeholders.

### Session 9 — Strip module numbering from code_base

* Rename module folders to drop the `mNN_` numbering prefix (e.g. `m01_data_acquisition` → `data_acquisition`), and update all cross-module imports and any string-based path references accordingly. Isolated to its own session given unknown blast radius across cross-module imports — run once other renames have landed and settled, not concurrently with them.

---

## Part 2 — Passed to the Main Refactor

* Type coercion at the CSV/ProjectState boundary is currently ad hoc (fixed once, for `enabled`) rather than systematic. Worth a single normalisation step applied uniformly at every Running Order entry point, or a move to typed dataclasses for Running Order rows instead of raw dicts.
* Allow a single `.cgp` file to draw on multiple TBN projects, including projects hosted on different databases — which may require ChartGen to hold more than one set of credentials at once.
* `.cgp` file association and installer — natural fit once the application is judged stable enough for wider distribution.
* Text Engine and Batch Controller as dedicated modules — flag token replacement and the batch iteration loop are currently not split into their own module folders. Planned as part of the refactor.
* Modular structure — including insertions (e.g. proposed `m15_insertions`, which would house toolkit hyperlink insertion — not built) — to be discussed as part of the refactor.
