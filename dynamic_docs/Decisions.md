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

## Session 8 — [Date not specified]

**Decision:** `PopulationShape` is retired as a distinct wrapper type. `population_label` is added as a native field directly on `NumericSeries`, `NumericCompositional`, and `CategoricalCompositional`; `role` is dropped entirely rather than kept as `population_role`.
**Rationale:** User's framing — a data shape is by definition always a comparative dataset for some population, so a `PopulationShape` wrapper was never a distinct concept, just a data shape with two extra fields bolted on. Walking through `build_population_shapes`'s actual resolution code together showed `role` carried no information `label` didn't already have: identical to `label` for `All`/`Selected` tokens, and just the raw unresolved token text (not a real category) for peer-group tokens. Since chart-highlighting logic only ever needed to distinguish "is this Selected," `population_label == "Selected"` preserves that exact check with nothing lost.

**Decision:** `base_charts.py` was updated only mechanically (attribute access changed, no logic touched) to keep it working against the new data shape, rather than rewritten or improved as part of this session.
**Rationale:** Explicit user instruction — `base_charts.py` is flagged as due for a full rewrite in a future session; this session's job was to make it "accept" the new structure, not to fix or improve it. A dead, uncalled helper (`_layer_colour`) was noticed during the mechanical pass and left alone rather than removed, consistent with staying strictly in scope.

**Decision:** Reference document updates for this session were kept deliberately short, describing the new `population_label` behaviour without expanded rationale or examples beyond what already existed.
**Rationale:** Explicit user instruction — "keep that really short and concise... we should be simplifying behaviour" — treated as a standing steer for this specific documentation pass, not a change to the general Docs Maintenance Guide style rules.

## Session 9 — [Date not specified]

**Decision:** The immediate priority for this session is a single user losing their own unsaved work by closing the browser, not two users editing concurrently — despite "Concurrency review" being the session's pre-planned title.
**Rationale:** User's explicit reframing after the initial review — the advisory lock mechanism only ever concerns a second opener; it does nothing for the more common failure mode of one person closing the browser without saving. Both problems were worked on this session, but as two genuinely separate mechanisms, not folded into one.

**Decision:** A `beforeunload` browser warning on tab close is wanted, but was not implemented this session.
**Rationale:** Agreed as a small, self-contained, low-risk addition (native browser prompt, gated on `ws.dirty`, no dependency, doesn't touch the lock). The conversation moved to the Read-Only/decision-screen request before it was built. Carried forward as outstanding, not rejected.

**Decision:** Autosave/checkpoint mechanisms and a full idle-timer autosave were discussed as options but not pursued further this session.
**Rationale:** Raised as part of the same "forgot to save" discussion as the `beforeunload` warning; the user did not pick either up as a next step. Not rejected outright — worth raising fresh rather than assuming a verdict either way.

**Decision:** Opening a workfile always routes through a decision step in the main body offering **Open** or **Open Read-Only**, even when the file is not locked, rather than opening a clean file directly as before.
**Rationale:** User's explicit request — Read-Only needed to be available on a clean file too ("if it's clean, I'd like the option of a read-only version"), not just as a locked-file fallback. Reusing one decision screen for all three lock states (clean / same-user / different-user), varying only the message shown above the buttons, was agreed as sufficient rather than building three separate flows — the user confirmed the same-user case should route to the same Open/Open Read-Only choice rather than a bespoke path.

**Decision:** The same-user warning (locked by the current user) states that the file "was not closed down properly last time, or may still be open elsewhere under your account," holding both possibilities rather than asserting one.
**Rationale:** The lock alone cannot distinguish a crashed/uncleanly-closed prior session from a genuinely live one elsewhere (another tab, another machine, under the same account) — there is no liveness signal anywhere in the system. Asserting either explanation with confidence would be misleading.

**Decision:** Read-Only enforcement is shallow: only the Save button is disabled. Every other tab and action behaves exactly as in a normal session, so unsaved edits made in a read-only session are genuinely lost if not rescued via Save As.
**Rationale:** User's explicit choice, drawing a direct parallel to Word and Excel's own read-only behaviour — "edit and lose" is the accepted model there, and there was no appetite for the much larger effort of gating every mutating widget across every tab individually.

**Decision:** Save As remains available in a Read-Only session and is the only way out of it. It must target a folder different from the original workfile's folder (checked via directory comparison, not filename), and a successful Save As converts the session to a normal editable one — lock written at the new path, `read_only` cleared.
**Rationale:** The different-folder requirement's real purpose, established through discussion, is avoiding two independent workfiles sharing the same `outputs/pptx`/`outputs/pdf` folder and mixing reports — not preventing `.cgw` overwrite, which the exact-path check already handled before this session. Converting to a normal session on successful Save As mirrors Word/Excel's own read-only-to-editable transition once a copy is saved elsewhere.

**Decision:** A read-only session's Save As does not release the lock on the original file when moving away from it, unlike an ordinary (non-read-only) Save As, which does.
**Rationale:** A read-only session never claimed that lock via `write_lock` in the first place, so clearing it on the way out would release a lock that may still genuinely belong to someone else (or, in the same-user case, one whose status the app can't actually verify). Only a session that itself holds the lock is entitled to release it.

**Decision:** No "save changes?" confirmation is shown when closing a Read-Only session via Close Without Saving or Sign Out, even with unsaved edits present.
**Rationale:** Proposed and explicitly rejected by the user — clicking Close or Sign Out is itself the decision and shouldn't be second-guessed. Also reasoned through as avoiding an inconsistency: since the tab-close path can never offer a save-changes prompt (no hook exists for it), adding one only to the in-app buttons would have made Read-Only's behaviour depend on which way the user chose to leave, which was judged worse than offering the confirmation nowhere.

**Decision:** The persistent Read-Only indicator is a plain "READ-ONLY" label next to the "ChartGen" heading, with no name or timestamp shown alongside it.
**Rationale:** User's explicit distinction — the label describes the file's current behaviour for the rest of the session, not the history that led to it. Who/when detail was already shown once, at the point the user chose to open read-only; repeating it in a persistent element would be restating the past rather than describing the present.

**Decision:** The existing "dirty" terminology is not reused for the lock-not-cleanly-closed state; "locked" is used instead.
**Rationale:** `WorkfileState.dirty` already has an established, different meaning (unsaved in-memory changes within the current session). The user's own proposed term for the new concept risked colliding with that; "locked" was adopted instead, aligning with the pre-existing `locked_by`/`locked_at` fields it actually describes.

**Decision:** Reference document updates for Session 6 (Architecture, Functional Spec, Feature List, Refactoring Issues) are deferred to the next session rather than written now.
**Rationale:** User confirmed the decision-screen and warning message wording is a first draft likely to be revised. Documenting exact copy now risks an immediate rewrite; the underlying decision logic (lock states, Read-Only scope, Save As folder rule) is stable and won't need re-doing regardless of wording changes.

## Session 10 — [Date not specified]

**Decision:** `organisations.csv` storage is removed entirely rather than reconsidered or redesigned.
**Rationale:** Traced its complete lifecycle and found no consumer beyond the point of creation — organisation data is fetched once, used immediately in memory to resolve `Region()` onto `units.csv`, and the separately-persisted copy was never read again by anything. User's stated driving principle: clean data flows with minimal intermediary stages: a store that is written and read back but never consulted is the opposite of that, regardless of how it could be redesigned.

**Decision:** No detection or cleanup code was added for the stale `organisations.csv` that pre-existing `.cgw` files retain from before this change.
**Rationale:** Explicit user instruction — "the process of removing it means our system would need code acknowledging its existence. Our driving focus is simplification." Writing code to find and strip a legacy artifact would reintroduce the same category of unnecessary complexity being removed, just aimed at old files instead of new ones.

**Decision:** When removing something from the codebase that should never have existed (as distinct from retiring something that legitimately did), the reference documents are edited as if it was never there — deletion, not a recorded change — except for Refactoring Issues, which records the removal as its normal function.
**Rationale:** Explicit user instruction, given after an initial documentation pass recorded the `organisations.csv` removal descriptively across all docs. User's framing: "the problem was the existence of something that shouldn't have been there," so the fix is to check whether it was documented and remove that documentation, not to narrate its removal — Architecture, Functional Spec, Feature List, and Glossary describe current ground truth only, and this thing was never legitimately part of that truth. Refactoring Issues is treated differently because tracking what happened, including mistakes corrected, is its stated purpose.

**Decision:** `_is_chart_placeholder`'s type whitelist is widened to 8 native PowerPoint placeholder types (`OBJECT`, `PICTURE`, `CHART`, `BITMAP`, `TABLE`, `ORG_CHART`, `MEDIA_CLIP`, `BODY`), rather than expanded to the full ~20-member `PP_PLACEHOLDER` enum or narrowed further.
**Rationale:** User's stated aim was covering every placeholder type a human designer would plausibly pick from PowerPoint's own Insert Placeholder UI (Content, Picture, Chart, Table, SmartArt, Media, Text) for a chart/picture/table content slot, while excluding role-specific text placeholders (Title, Subtitle, Center Title, Date, Footer, Header, Slide Number, vertical variants) that are, in the user's words, "small defined task orientated placeholders" no human would repurpose for "a big chunky piece of content."

**Decision:** The name-based classification bypass (`shape.name.lower().startswith("chart")`) is removed entirely. A placeholder is now recognised purely by `shape.is_placeholder` + native type membership in the whitelist — never by name.
**Rationale:** User's explicit instruction, following the same discussion — with the whitelist widened to cover every realistic content-bearing type, the name-based escape hatch no longer serves a purpose it can't already cover by type, and its presence was itself the source of the original silent-miss risk (an unlisted type could only be rescued by naming, so an unlisted, unnamed placeholder failed invisibly). Confirmed via `running_order.py` that no other code path depends on placeholder naming for anything beyond Running Order row display, before making the change.

## Session 11 — [Date not specified]

**Decision:** Session 9 (module numbering strip) was executed as a pure mechanical rename — folder names stripped of `mNN_` only, no other renaming — after a full blast-radius scan (34 references, including 2 string-built paths) rather than an incremental rename-and-fix-as-you-go approach.
**Rationale:** Scanning first isn't extra process — the scan is a prerequisite either way, since renames can't be done safely without knowing every reference. Doing it upfront in one pass avoids discovering breakages one at a time. User confirmed this approach before starting.

**Decision:** Documentation updates for the module rename used simple search-replace only, with no additional review or restructuring, per explicit user instruction to keep it simple and avoid overthinking.
**Rationale:** User instruction, citing limited remaining tokens. Only Architecture and Glossary needed changes (module tree/table); Refactoring Issues was deliberately left with the old names as a historical record.

**Decision:** This session's close-down skipped testing/thinking stages and the Project Files verification step (Close-down protocol step 7), per explicit user instruction due to low remaining tokens.
**Rationale:** User instruction. Documented here so a future session doesn't assume verification happened.


## Session — 2026-07-08

- Pruned three Part 2 Refactoring Issues items (beforeunload warning, autosave/checkpoint mechanisms, advisory-lock re-check gap) — no longer worth tracking.
- Decided to pull the Part 2 "type coercion at the CSV/WorkfileState boundary" item into pre-factor as a deliberate, one-off exception to the otherwise strict Part 1/Part 2 boundary, rather than leaving it for the main refactor or opening it as a formal Part 1 session.
- Decided the coercion fix should be a shared `FIELD_TYPES` table + one `coerce_row()` function, applied at the true point of origin (the API boundary in `api_client.py`) rather than typed dataclasses — dataclasses remain a separate, larger Part 2 question (untyped dicts item), not folded into this fix.
- Decided not to add coercion at the settings.csv boundary despite it being named in the original proposal — inspection showed no actual type inconsistency there (`batch_cursor`'s existing single cast site already works), and adding a no-op call would add complexity without fixing anything.
