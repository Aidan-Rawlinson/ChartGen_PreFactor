<!-- Purpose: Claude's handoff note -- what to pick up, open questions, and suggested first steps for the next session. Written by Claude at session end. -->

## Suggested first step

Start Refactoring Issues Session 9 — strip module numbering from `code_base`. This is the last item in Part 1 before the pre-factor plan is fully worked through. Per its own scope note, it's isolated to its own session given unknown blast radius across cross-module imports, and should run now that all other renames have landed and settled.

Scope, per `Refactoring_issues_known.md`:
- Rename module folders to drop the `mNN_` numbering prefix (e.g. `m01_data_acquisition` → `data_acquisition`), and update all cross-module imports and any string-based path references accordingly.
- Mechanical flat rename plus reference clean-up only — does not include designing or introducing nested sub-packages (that's Part 2, "Modular structure").
- Refer to modules by name, not number, throughout documentation, once the code-side names are final.

## Open questions for the user

None outstanding — Sessions 6, 7, and 8 are all fully resolved with no deferred decisions.

## Notes for continuity

- **Module inventory for Session 9:** `m01_data_acquisition`, `m02_template_reader`, `m03_running_order`, `m04_data_shapes`, `m05_chart_engine`, `m06_assembly_engine`, `m07_insert_picture`, `m08_insert_from_excel`, `m09_static_config`, `m12_local_config`, `m14_workfile_file`, plus the non-numbered `constants_temp`. `m10`/`m11`/`m13` no longer exist (m10/m11 retired in Session 1; m13 was never used) — the live sequence skips numbers, which is itself part of what Session 9 resolves by dropping numbering entirely.
- Check for string-based path references before assuming a straightforward import rename covers everything — e.g. anywhere a module path is built as a string (`os.path.join`, dynamic imports) rather than a plain `import` statement, since those won't be caught by an IDE-style rename.
- Once module folders are renamed, the documentation-side task (referring to modules by name not number) should be done in the same session, per the Refactoring Issues item's own note that both sides "should land together once the code-side names are final."

- **`organisations.csv` is gone — don't reintroduce it or code that detects it.** `WorkfileState.organisations` no longer exists. Organisation data is fetched once at New Workfile creation (`get_organisations` in `app.py`), joined in memory to resolve `Region()` onto `units.csv`, and discarded — this is now the only place organisation data is touched. Pre-existing `.cgw` files may still contain a stale `organisations.csv` inside them; this is deliberately not detected, stripped, or migrated. If this comes up again, the standing decision is to leave it alone.
- **Documentation philosophy established this session, worth carrying forward:** when removing something that shouldn't have existed (as opposed to changing something that legitimately did), the reference documents (Architecture, Functional Spec, Feature List, Glossary, Primer) should be edited as if it was never there — deletion, not a recorded change — since those documents describe current ground truth only. Refactoring Issues is the exception, since recording what happened is its actual job. Apply the same test if a similar "this shouldn't be here" cleanup comes up again.
- **Placeholder recognition is now purely type-based.** `_is_chart_placeholder` (`template_reader.py`) checks `shape.is_placeholder` plus `shape.placeholder_format.type` against an 8-type whitelist (`OBJECT`, `PICTURE`, `CHART`, `BITMAP`, `TABLE`, `ORG_CHART`, `MEDIA_CLIP`, `BODY`). There is no name-based classification anywhere in this function anymore — don't reintroduce a name-starts-with-"chart" shortcut. Placeholder names are still read and stored (`PlaceholderInfo.name`) but only for Running Order row display.
- `settings["workfile_folder"]` is still not populated anywhere in `app.py` — a pre-existing functional gap, unrelated to any of this session's work, not fixed.
- `constants_temp` (`modules/constants_temp/constants_temp.py`) now holds only `UNITS_FIELDNAMES` (its `ORGANISATIONS_FIELDNAMES` sibling was removed this session along with the store it described). Still deliberately temporary; see Refactoring Issues Part 2 for its likely permanent destination.
- `unit_id` is `str` everywhere. `organisation_id` still has the same unaddressed int/string inconsistency (Refactoring Issues Part 2) — not yet fixed.
- Peer groups remain a single mechanism — every peer group is a `Name()` column; `x`/blank both mean no group, treated identically everywhere. Population resolution remains scope-plus-independent-layers (Session 4/6 decisions), and `PopulationShape` remains retired in favour of native `population_label` (Session 5/8 decisions) — no changes to either this session.
- `app.py` still has an open Part 2 refactor item flagging it needs a full content review — untouched this session beyond the New Workfile flow edit for Session 7.
