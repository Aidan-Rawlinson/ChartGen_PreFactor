<!-- Purpose: Significant decisions and the reasoning behind them. Kept separate so rationale does not get buried in the Progression_Log. -->

## Session 1 — [Date not specified]

**Decision:** Mid-session documentation write behaviour (writing approved edits to the mirror immediately, rather than batching to Close-down) is governed by a new Section 8 in `ChartGen_Docs_Maintenance_Guide.md`, not by changes to the Session Start or Close-down protocols in Project Instructions. Project Instructions gained only a one-line pointer to that section.
**Rationale:** The Guide already owns "how edits to the six docs happen"; this is the missing piece about *when* they're written to disk during a session, not a change to session bookends. Session Start and Close-down protocols must remain untouched per explicit user instruction.

**Decision:** The Refactoring Issues log is split into two parts: items handled within the ChartGen_PreFactor project (grouped into 9 sessions) and items passed forward to the main refactor.
**Rationale:** Some issues are genuine pre-refactor cleanup (dead code, doc fixes, terminology, contained structural changes); others are foundational architecture work or net-new features that belong with the main refactor effort once it starts.

**Decision:** `organisations.csv` storage reconsideration, binary peer group review logic, and explicit-value peer group tokens (`Region(Wales)`) are handled in this project, not deferred to the main refactor.
**Rationale:** User judged these genuine, contained refactors suitable for pre-refactor cleanup rather than requiring the main refactor's broader scope.

**Decision:** Stripping module numbering from the actual `code_base` folder/import structure is a standalone session (Session 9), run last, separate from the doc-only module-numbering fix (Session 1).
**Rationale:** Unknown blast radius across cross-module imports and possible dynamic path construction; safer to isolate and run once other renames have already landed, rather than compounding risk mid-flight.

**Decision:** "Item table" terminology renames to "Population table" (not "Unit table").
**Rationale:** "Population" is the stronger human-facing term; "Unit" reads as weak outside the codebase. (Carried forward from the pre-existing Refactoring Issues log, reaffirmed during this session's categorisation.)

**Open decision (not yet made):** Replacement terms for "Flag token" and "Batch" terminology — both disliked but no alternative agreed yet. To be resolved at the start of Session 3 before renaming.

## Session 2 — [Date not specified]

**Decision:** When a Refactoring Issues item is resolved, mark it resolved in place (strikethrough + "Done — ...") rather than deleting the line.
**Rationale:** Explicit user instruction, given after the first resolved item (`Claude_Please_Check.md`) was initially deleted outright — the log should retain visible history of what was done, not just what remains.

**Decision:** The "module numbering incorrect" and "refer to modules by name not number" items (originally Session 1) are folded into Session 9 rather than actioned as doc-only fixes now.
**Rationale:** User judged the underlying rename conceptually simple in a fully working codebase, and Session 9's flat rename will resolve/supersede both directly — no value in fixing the numbering or the docs separately first.

**Decision:** Session 9 remains pre-factor scope only — a mechanical flat rename of module folders (dropping the `mNN_` prefix) plus reference clean-up. It explicitly excludes designing or introducing nested sub-packages.
**Rationale:** Discussion with the user established that genuine nested substructure (e.g. a `chart_engine/tweaks/` split) is a structural/design decision with load-bearing consequences for future work — main-refactor territory, not a pre-factor cleanup step. Logged separately in Part 2 under "Modular structure."

**Decision:** New Refactoring Issues Session 10 (Docstring protocol and review) created.
**Rationale:** The `running_order.py` docstring fix established a working principle (state purpose/contract; cross-reference enumerable detail rather than restate it) by example by not by policy. Worth formalising and sweeping the rest of the codebase for the same drift pattern.

**Decision:** `SUBMISSIONS_FIELDNAMES`/`ORGANISATIONS_FIELDNAMES` moved to a new, explicitly temporary module `constants_temp`, rather than into `m14_project_file` or `m04_data_shapes`.
**Rationale:** `m14_project_file`'s own contract is narrow — "no other module touches the ZIP directly" — and doesn't extend to owning record-shape schema that `app.py` also depends on independently of persistence. `m04_data_shapes` was ruled out because it currently mixes pure data structures with filter/recalc operations (`filter_shape`, `_recalc_*_stats`), failing the user's stated condition that a destination module contain "nothing other than reference." Logged in Part 2 as needing a permanent home once that split happens.

**Decision:** `submissions_to_display_rows` moved into `app.py` (nested inside the Select tab, renamed `_submissions_to_display_rows`) rather than to any module.
**Rationale:** Confirmed it has exactly one caller, touches no `ProjectState` data, and does pure UI-shaping (unpivoting pipe-delimited service columns for one dataframe toggle) — matches the file's existing convention for tab-local display helpers (`_submission_label`, `_short_func`, `file_label`). No module boundary was actually being served by keeping it separate.

**Decision:** `m10_project_config` retired entirely (folder deleted) once its last remaining function was relocated.
**Rationale:** Following the above two decisions, nothing legitimately belonging to the module remained — an empty module wearing the last name tag was judged worse than no module at all.

## Session 3 — [Date not specified]

**Decision:** `WorkfileState.project_name` renamed to `workfile_name` (and the matching UI label, "Project name" → "Workfile name", in the New Workfile and Save As forms), rather than left as `project_name` or flagged ambiguous.
**Rationale:** This field stores the file-facing name used to build the `.cgw`/`.pptx` filenames — structurally distinct from `settings["project_name"]` (the TBN project selected via the toolkit API), which lives in a different dict entirely. The two were never actually the same concept sharing a name by coincidence of UI copy, not a genuine conflation requiring a design decision.

**Decision:** "Project Details" tab title, "Import Project Data" tab title, and `settings["project_name"]`/`settings["project_id"]` are TBN-project references and are not renamed to "Workfile".
**Rationale:** Explicit user confirmation after these three were surfaced as ambiguous/mixed cases. The Details and Imports tabs display TBN project identity fields directly; the settings keys are populated from the TBN projects API.

**Decision:** `settings["project_folder"]` renamed to `workfile_folder` despite being unpopulated anywhere in `app.py` (a pre-existing gap), rather than left alone or fixed.
**Rationale:** The key's only two consumers (`assembly_engine._ensure_output_folder`, `insert_from_excel`'s error-log path) both treat it unambiguously as "the folder alongside the workfile" — same concept as the `_workfile_dir`/`_cgp_dir` pattern already used elsewhere in `app.py`. Renaming is a naming-correctness fix; the fact that nothing populates it is a separate, pre-existing functional gap logged for awareness, not addressed now since it wasn't part of the requested rename.

**Decision:** The "M10/M11 status" paragraph and module-tree entries for `m10_project_config`/`m11_data_cache` were removed from Architecture and Glossary, rather than updated in place.
**Rationale:** Both modules were fully retired in the prior session (Refactoring Issues Session 1). A "current system" architecture document has no reason to describe modules that no longer exist; the historical record of their removal already lives in Refactoring Issues Session 1's entry, so restating it in Architecture was pure duplication once the modules were gone rather than merely dead-code-flagged.

## Session 4 — [Date not specified]

**Decision:** Refactoring Issues Session 10 (Docstring protocol and review) was executed ahead of Session 3, resequencing the pre-planned Part 1 order.
**Rationale:** User request at session start; no dependency forced Session 3 to go first, and the docstring pass was judged quick, low-risk, and doc-adjacent.

**Decision:** Final docstring protocol — a docstring states only identity (what a module/function is or does), never mechanics, rationale, design intent, roadmap language, or cross-references to other documents or constants; length target of 1 sentence, 2 only with strong justification (e.g. a necessary caller-facing caveat).
**Rationale:** Agreed iteratively with the user across several rounds of discussion. Explicitly reverses the Session 1 `running_order.py` docstring, which had cross-referenced Architecture/Functional Spec — that pattern is superseded, not extended.

**Decision:** Untyped dict/row contracts with no type or schema defined elsewhere (API response shapes, Running Order row fields, yellow-box classification, the populations-string token legend) are a deliberate exception to the "no schemas" rule and are kept in docstrings.
**Rationale:** User judged that cutting these loses information with no other home — nothing else in the codebase currently documents these shapes. Logged as a Part 2 open question on whether these should become typed structures instead, which would let the exception be retired.

**Decision:** Dataclass field-position/semantics documentation (e.g. `NumericSeriesUnit.values[i]` correspondence to `metric_names[i]`, `PopulationShape.role`/`label` string-value meaning, `CategoricalCompositionalUnit.response` meaning) does **not** get the same exception as the dict/row contracts, and was cut.
**Rationale:** User's explicit ruling — although the same underlying problem (no type captures the meaning) applies, these are dataclass fields rather than untyped dicts/rows, and the general "cut" rule was judged to still apply.

**Decision:** The disputed accuracy of `running_order.py`'s `read_xlsx` docstring (claims it skips `enabled == 0` rows; code appears not to) was not investigated, fixed, or logged as a bug — the docstring was left as-is since it already fit within the 2-sentence limit.
**Rationale:** User was skeptical of the claimed discrepancy and asked for it to be dropped entirely, with no special handling — treated as an ordinary docstring under the normal length rule rather than a code-correctness question.
