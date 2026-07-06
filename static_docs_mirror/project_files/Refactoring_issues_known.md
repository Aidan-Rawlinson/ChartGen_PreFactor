# ChartGen — Refactoring Issues (Known)

This document is split into two parts: items being handled in the ChartGen_PreFactor project (grouped into focused sessions), and items being passed forward to the main refactor.

---

## Part 1 — This Project (ChartGen_PreFactor)

### Session 1 — Quick wins (dead code + doc-only fixes)

* ~~Legacy disk-fallback code in M10/M11.~~ Done — traced every disk-fallback branch and helper against live call sites, confirmed all unreachable on the `ProjectState` path, and removed them: the dead branches/constants in `cache_writer.py`, `fetch.py`, `url_parser.py`, and `cache_reader.py`; `m10_project_config/settings.py` in full plus the orphaned `settings.csv`/`urls.csv`; the empty `m11_data_cache/` folder. This also surfaced two follow-on structural fixes — see Decisions log — resulting in the retirement of `m10_project_config` entirely and the creation of `constants_temp` (Part 2).
* ~~Debug tab (Debug Trace) — never used in practice.~~ Done — removed from `app.py` and the Functional Spec.
* ~~Delete `Claude_Please_Check.md` from the repository — references superseded document names.~~ Done — deleted from the repository.
* ~~Stale module docstring in `m03_running_order/running_order.py` — documents the old 12-column schema and an outdated function list.~~ Done — docstring trimmed to purpose and contract; column schema and function categories now cross-referenced to `COLUMNS`/`STRUCTURAL_FUNCTIONS`/`CONTENT_FUNCTIONS`/`BATCH_FUNCTIONS` and to Architecture §4 / Functional Spec §9.2, rather than restated. (Superseded by Session 10 — the docstring protocol agreed there disallows cross-referencing; this docstring has since been trimmed further.)

### Session 2 — Workfile rename

* ~~Terminology — "Project" collides with TBN's own usage (a benchmarking exercise/data source). Rename the ChartGen-file-lifecycle concept to "Workfile" throughout code and documentation.~~ Done — scope as landed:
  - The architectural concept — the "Project domain" (Architecture §2, §4, §5) is now the "Workfile domain".
  - The in-memory object — `ProjectState` is now `WorkfileState` (field `cgp_path` → `workfile_path`; `project_name` → `workfile_name`).
  - File/folder naming in the codebase and archive — `.cgp` extension → `.cgw`; `m14_project_file`/`project_file.py` → `m14_workfile_file`/`workfile_file.py`; internal `project_info.json` → `workfile_info.json`; internal `project_config/` folder → `workfile_config/`. (`m10_project_config` no longer exists — retired in Session 1 — so that part of the original scope no longer applied.)
  - Generic prose and UI — "opening a project", "project data", "dirty project", "no-project-loaded state", sidebar button/dialog labels ("New Project"/"Open Project" → "New Workfile"/"Open Workfile"), lock warning text, etc.
  - Settings key `project_folder` → `workfile_folder` (used by the Assembly Engine and Insert-From-Excel for the folder alongside the workfile). Note: this key is still not populated anywhere in `app.py` — a pre-existing gap, unrelated to the rename, not fixed here.
  - **Decided to leave as TBN references, not renamed:** the "Project Details" and "Import Project Data" tab titles (Functional Spec §3.2), and the `settings["project_name"]`/`settings["project_id"]` keys. These sit unprefixed in the same settings dict as workfile-scoped keys (`cleaned_template_path`, etc.) with nothing distinguishing the two origins — not acted on now, but worth bearing in mind in any future settings-dict rework.
  - "New Project flow" → "New Workfile flow" throughout, keeping "year and project selection" wording intact where it refers to the TBN project pick within that flow.
  - The five reference documents (Architecture, Functional Spec, Glossary, Feature List, this issues log) have been brought into line with the code in this same pass.
  - "Project root" (Decision 9, Architecture) — the disambiguation this session originally flagged (a third, unrelated sense meaning the software installation folder) was checked against the current Architecture document and codebase; the phrase doesn't currently appear anywhere. Likely stale from an earlier draft — noted here rather than silently dropped.
  - Out of scope, confirmed unchanged — genuine TBN usage of "project" (`project_id`, `project_name`, the TBN projects API, "Project Summary Report", etc.).

### Session 3 — Remaining terminology renames

* "Comparative unit" / "comparative population" → "Unit" / "Population" — Documentation settles on plain "Unit" and "Population" as the standard terms (per the Primer), with "Reporting Unit" retained as a named special case of Unit. Codebase currently uses the compound form throughout: the `ComparativeUnit` class (`m04_data_shapes/shapes.py`) and its subclasses, "comparative population" in docstrings, and a stray "comparator population" string in the `app.py` UI caption. All require updating to match — class rename, docstring updates, and the one leftover UI string, which was already inconsistent with the Primer's own stated convention before this decision.
* "Item table" terminology — "item" is an early, superseded name for what is now called "Unit"/"Reporting unit". Appears in `app.py` (a UI caption and an expander label, "Submissions — item table") — the `m10_project_config/submissions.py` docstring instance no longer applies, since that module has been retired and its one live function now lives in `app.py` directly. Rename throughout code and documentation to **Population table** — decided in preference to "Unit table," since "Population" is the stronger human-facing term and "Unit" reads as weak outside the codebase.
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

* Module numbering incorrect — the current sequence skips `m13` (`m01`–`m12`, then `m14`). Superseded by the rename below rather than fixed in place: once the `mNN_` prefix is dropped entirely, there's no numbering left to be wrong. (Note: `m10` and `m11` have since been retired entirely during pre-factor — see Session 1 and Part 2 — so the live sequence is narrower than originally scoped.)
* Rename module folders to drop the `mNN_` numbering prefix (e.g. `m01_data_acquisition` → `data_acquisition`), and update all cross-module imports and any string-based path references accordingly. Isolated to its own session given unknown blast radius across cross-module imports — run once other renames have landed and settled, not concurrently with them. Pre-factor scope only — a mechanical flat rename plus reference clean-up; it does not include designing or introducing nested sub-packages (see Part 2, "Modular structure").
* Refer to modules by name, not number, throughout documentation — module numbers are not maintainable over time. Folded in here since it's the same clean-up performed on the documentation side rather than the codebase side, and both should land together once the code-side names are final.

### Session 10 — Docstring protocol and review

* ~~No consistent policy exists yet for what a module/function docstring should and shouldn't contain. The `m03_running_order/running_order.py` fix (Session 1) established a working principle by example — docstrings state purpose and contract; anything mechanically enumerable (schemas, function lists, column definitions) is cross-referenced to the code constant and/or the owning reference document (Architecture/Functional Spec) rather than restated in prose — but this hasn't been written down as a standing rule, and no other module's docstrings have been checked against it.~~
* ~~Scope: agree and record the policy, then review every module's docstrings across the codebase for the same class of drift (duplicated schemas, stale function lists, restated facts that already live in a constant or a reference document), fixing each on the same pattern.~~

Done — policy agreed and applied:
  - A docstring states only identity — what a module/function is or does — never mechanics, rationale, design intent, roadmap language, or cross-references to other documents or constants. This supersedes the Session 1 `running_order.py` example above, which cross-referenced Architecture/Functional Spec; that is no longer the pattern.
  - Length target: 1 sentence; 2 with strong justification (e.g. a necessary caller-facing caveat).
  - Exception: untyped dict/row contracts with no type or schema defined anywhere else (API response shapes in `api_client.py`/`fetch.py`, Running Order row fields in `insert_picture.py`/`insert_from_excel.py`/`assembly_engine.py`, yellow-box classification in `template_reader.py`, the populations-string token legend in `assembly_engine.py`) are kept in docstrings, since cutting them would lose information with no other home. See Part 2 for the governance question this raises.
  - Every module and function docstring across the codebase has been reviewed and brought into line with this policy in this session.

---

## Part 2 — Passed to the Main Refactor

* Type coercion at the CSV/WorkfileState boundary is currently ad hoc (fixed once, for `enabled`) rather than systematic. Worth a single normalisation step applied uniformly at every Running Order entry point, or a move to typed dataclasses for Running Order rows instead of raw dicts.
* Several functions pass data as untyped dicts rather than dataclasses (API responses, Running Order rows, fetch results, yellow-box classification). Their shape currently exists only in docstrings and call-site usage, not in any type. Given the vibe-coded origin of this codebase, worth a dedicated discussion on whether these should become typed structures (dataclasses/TypedDicts) for accountability — which would also let docstrings drop the schema enumeration currently kept there as a stopgap (see Session 10).
* Allow a single `.cgw` workfile to draw on multiple TBN projects, including projects hosted on different databases — which may require ChartGen to hold more than one set of credentials at once.
* `.cgw` file association and installer — natural fit once the application is judged stable enough for wider distribution.
* Text Engine and Batch Controller as dedicated modules — flag token replacement and the batch iteration loop are currently not split into their own module folders. Planned as part of the refactor.
* Modular structure — nested sub-packages for modules with genuine internal substructure (e.g. a `chart_engine/tweaks/` split for reference lines, axis control, conditional colouring; possible equivalents elsewhere such as `assembly_engine`'s Excel-COM logic or `insert_from_excel`), plus the previously proposed `m15_insertions` for toolkit hyperlink insertion (not built) — to be designed and discussed as part of the refactor, not pre-factor.
* `constants_temp` module needs a permanent home. Created as a pre-factor stopgap to hold `SUBMISSIONS_FIELDNAMES`/`ORGANISATIONS_FIELDNAMES` — moved out of `m10_project_config` once that module stopped doing any I/O and had no legitimate claim to own record-shape constants that `m14_workfile_file` (serialisation) and `app.py` (New Workfile flow) both depend on as peers. Likely permanent destination: a definitions-only module, once `m04_data_shapes` is split into pure data structures (`NumericSeries`, `ComparativeUnit`, `PopulationShape`, etc.) versus the filter/recalc operations (`filter_shape`, `_recalc_*_stats`) that currently live there alongside them — `m04_data_shapes` cannot host these constants as-is without contradicting the "reference-only" condition that motivated moving them out of M10. `constants_temp` is a working name only, not meant to survive into the main refactor.
* `app.py` needs a genuine content review. Through pre-factor cleanup it's become clear `app.py` is not just a thin Streamlit gateway — it now also holds display-shaping logic that arguably belongs to the interface layer but isn't organised as one (e.g. `_submission_label`, `_submissions_to_display_rows`, both nested inline in the Select tab, following the pattern already set by `_short_func` in the Running Order tab and `file_label` in the Charts tab). `m10_project_config`'s retirement is what surfaced this: its last remaining function turned out to be UI-only and was moved into `app.py` rather than to another module, because nothing else fit — a sign `app.py` may need its own internal structure (or a genuine UI-helpers module) rather than continuing to accumulate inline nested functions per tab. Scope for the main refactor: inventory everything currently living in `app.py` beyond Streamlit wiring itself, and decide what — if anything — should be extracted, and to where.
