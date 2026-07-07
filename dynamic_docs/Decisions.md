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

## Session 5 — [Date not specified]

**Decision:** "Flag token" renamed to "Text Tag".
**Rationale:** Agreed after distinguishing the token concept (the noun — the placeholder string itself) from "Text Replacement" (the activity name — what `update_text` does). "Replacement" is a nominalisation with both a process sense and a result sense, which was the actual source of the naming clash; "Text Tag" names the object without colliding with the activity name.

**Decision:** "Batch" terminology resolved as a split rather than a uniform rename: the Streamlit tab is renamed from "Batches"/"Batch Processing" to "Outputs" (short) / "Create Outputs" (long); `Run Selected`, `Run Batch`, `Run All`, and the internal batch-processing concept are unchanged.
**Rationale:** User's proposal — "batch" is machine-logical (a batch of 1 or of all is still a batch computationally) but a poor human-facing label for a tab whose purpose is producing reports, not literally "batching." `Run Batch` specifically was confirmed to stay as-is on the grounds that it is precisely the case where a human does mean "batch" — neither one (Run Selected) nor all (Run All).

**Decision:** The Submission/Unit rename boundary is drawn at the point of data ingestion: `api_client.py`'s `get_submissions()` function and the raw API JSON keys it reads (`submissionId`, `submissionCode`, `submissionName`) keep "submission" naming; everything from the point `app.py`'s New Workfile flow copies that data into `WorkfileState` onward uses "unit" naming (`unit_id`, `unit_code`, `unit_name`, `WorkfileState.units`, `units.csv`, `selected_unit_id`).
**Rationale:** User's explicit ruling, given as "normalisation" — the external API genuinely deals in submissions; the internal, normalised representation ChartGen builds from that data is the standardised Unit concept. This mirrors the codebase's existing normalisation principle (raw API data → canonical internal shapes) rather than introducing a new pattern.

**Decision:** Fields describing the submission event itself rather than unit identity — `submission_year`, `submission_level`, `submission_service_count` — were left unrenamed even though they live in the same row as the renamed identity fields.
**Rationale:** These describe *when*/*at what level*/*how much* was submitted, not *who* the unit is. "Submission" remains an accurate word for the event; only the identity fields (id/code/name) were in scope for the Unit rename.

**Decision:** `WorkfileState.submissions` renamed to `.units`, and the stored `submissions.csv` renamed to `units.csv`.
**Rationale:** Direct consequence of the Submission/Unit boundary decision above — confirmed explicitly with the user as two follow-on structural questions the field-level rename didn't answer on its own.

**Decision:** `settings["selected_submission_id"]` renamed to `selected_unit_id`.
**Rationale:** Sits on the same identity pattern as `submission_id`/`code`/`name` and is used throughout the Select and Outputs tabs to mean "which unit is currently selected" — confirmed with the user as an extension of the same boundary rather than a separate naming decision.

**Decision:** Downstream prose using "submission" to mean "reporting unit" (rather than the act of submitting) was also renamed for consistency, even though not explicitly named in the original Refactoring Issues text — "Multiple submissions from same org" → "Multiple units from same org" (Feature List), "Multi-submission table expansion" → "Multi-unit table expansion" (Feature List, Functional Spec §11.2).
**Rationale:** Both describe multiple *units* mapping to one org/table, not multiple submission *events* — the same identity-vs-event distinction that governed the CSV field renames, applied consistently to prose.

## Session 6 — [Date not specified]

**Decision:** Population stacking resolved as **scope-plus-independent-layers**: the first populations-string token defines the full comparison population (the scope); every subsequent token, including `Selected`, resolves independently against that scope rather than cumulatively against the previous token's result. This replaces the previously documented sequential-intersection model.
**Rationale:** User-derived from two competing real-world cases — `Welsh Hospitals^Small Hospitals^Selected` (where cumulative narrowing feels right) versus `All Trusts^Shelford Group^Selected` (where a non-Shelford trust legitimately wants to compare itself against the Shelford Group without being filtered out). Sequential intersection cannot express the second case at all — sibling peer groups intersected are mutually exclusive, so `All^East Midlands^West Midlands^Selected` would always empty out at the third token, yet showing two peer groups side by side against the full population was confirmed as a standard use case. Scope-plus-layers is the simplest model that supports both cases without a configurable mode.

**Decision:** Both `Selected` and peer-group layers resolve within the scope (the first token), not against the whole dataset.
**Rationale:** Explicit user confirmation — a report scoped to a population the reporting unit isn't part of is an authoring choice/error, and resolving everything downstream against the same scope keeps the model to one sentence: "the first token defines the population; every subsequent token is an independent subset of it."

**Decision:** An unresolvable or empty first token (the scope) returns no population shapes at all — no fallback substitution, no default population.
**Rationale:** Explicit user ruling — "an unresolvable first token returning no values is a valid result. We need to just accept that, not try to mitigate it here." Downstream, `insert_chart`'s pre-existing full-shape fallback (unchanged this session) still applies when `build_population_shapes` returns empty.

**Decision:** No warning mechanism was added for unresolvable tokens, empty resolutions, or the fallback-to-full-shape path, despite being raised as an option.
**Rationale:** Explicit user ruling, reiterated after being proposed twice — "the dominant way we will avoid these failures is clean data flows... we can't have our code ending up 50% covering situations that never occur." Silent-skip behaviour from the prior model is preserved as-is.

**Decision:** `unit_id` is standardised to `str` throughout the codebase (data shapes, `ReportContext`, resolution logic), coerced once at each ingestion boundary (`api_client.get_submissions`, the `transformers.py` chart-data transforms) rather than left as int or coerced defensively at each point of use.
**Rationale:** User's explicit reasoning — ids are identifiers, not quantities, and future data sources may only have non-numeric ids; a single canonical string type avoids the int/str boundary mismatch that was the actual cause of `Region()`/`Selected` resolving to zero units during testing (confirmed via a temporary debug dump, `population_debug.txt`, since removed).

**Decision:** The Excel `insert_from_excel` driver-range write (`driver_cell.Value = ctx.report_context.unit_id`) is left writing a string, not converted back to an integer.
**Rationale:** Explicit user instruction — Excel is expected to handle a numeric string in a driver cell without issue; to be confirmed by observation in practice rather than pre-emptively coerced.

**Decision:** The Running Order populations multi-select (`app.py`) was made fully generic — for every `Name()` peer-group column discovered in `units.csv`, it now offers the bare token plus one `Name(Value)` token per distinct value present in that column — rather than hard-coded to `Region()`/`Region(Value)` specifically.
**Rationale:** Explicit user correction after an initial fix was scoped too narrowly to region wording — "it must be a purely generic response not a specific one." Implemented as `get_peer_group_value_options` in `local_config.py`, with no column name referenced anywhere in the implementation.

**Decision:** During testing, a chart apparently failing to resolve `Region()`/`Selected` (zero units, despite correct string types) was traced to a year mismatch — `units.csv` built for 2025, chart data fetched against a different year's toolkit URLs — not a code defect. No code change was made in response; the resolution logic was confirmed correct once matching-year data was used.
**Rationale:** Established via ID-range comparison (chart data ids consistently ~4,000 below roster ids, a signature of two different years' submission ID sequences) and confirmed directly by the user. Recorded here so the apparent bug is not mistakenly revisited in a future session.

## Session 7 — [Date not specified]

**Decision:** There is no binary/flag peer group column type. Every peer group, including a simple yes/no group (e.g. Shelford Group), is authored as an ordinary `Name()` column, with a lowercase `x` (or a blank) marking units that don't belong to any group for that column — reversing the "flag columns" concept that had been documented in the Functional Spec and Feature List as a planned second mechanism.
**Rationale:** User-derived from two real cases: a cumulative-narrowing peer group, and Shelford Group, where a non-member should still be able to compare itself against the group without being filtered out. The key realisation was that "a unit and a peer group not intersecting" isn't unique to binary groups — an international trust with no `Region()` value is the same situation — so the binary type would have duplicated behaviour `Name()` columns already provide via blank values, rather than solving a distinct problem. Confirmed the binary type had never actually been implemented in `build_population_shapes`, so this is a documentation and design correction, not a deprecation of working code.

**Decision:** `x` and blank are treated identically everywhere a `Name()` column's value is read — both mean "no group for this unit" — rather than `x` carrying any distinct meaning (e.g. as a validation signal for missing data).
**Rationale:** User confirmed blank already does this for free (excluded from value discovery, resolves to no layer); giving `x` the same behaviour needed two explicit exception points added to code that otherwise wouldn't need them. The alternative — using `x` to catch genuinely missing/forgotten values — was raised and explicitly deferred as separate, new scope (a validation step), since it would require blank itself to become a flaggable state, which cuts against the clean-data-flows/no-warnings stance established in Session 6.
**Follow-on:** As peer-group-populating mechanisms are built in future sessions, they should write `x` rather than leaving cells blank, per the user's stated intent — "as we build the mechanisms for populating these fields we will make sure that they always read in with an x." Blank remains equally valid in the meantime.
