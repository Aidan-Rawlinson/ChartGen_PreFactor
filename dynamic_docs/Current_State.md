<!-- Purpose: A snapshot of where the project stands right now -- what works, what is in progress, what is broken. Rewritten by Claude each session. -->

## Status: In Progress — Refactoring Issues Session 6 (Concurrency review) — code complete, documentation pending

**Codebase:** `code_base/chartgen/` — a Read-Only path added to the existing advisory lock, plus a decision step on Open:

- `WorkfileState.read_only: bool = False` added (`m14_workfile_file/workfile_file.py`) — session-only, not persisted, same treatment as `dirty`. A read-only session never calls `write_lock`, so it never claims the advisory lock.
- `close_workfile` now returns immediately if `state.read_only` is set, before touching the lock — a read-only session must never clear a lock (its own stale one, or someone else's live one) that it never held.
- Opening a workfile (`app.py`, `_show_open_workfile_form`) no longer opens directly. It validates the path, then hands off to a new decision step (`_render_open_decision`) rendered in the main body, which reads `workfile_info.json` and shows one of three messages before offering **Open** or **Open Read-Only**:
  - Clean (no lock held): a neutral confirmation, no warning.
  - Locked by the current user: a warning that the file was not closed down properly last time, or may still be open elsewhere under their account — both are indistinguishable from the lock alone, so the message covers both possibilities rather than asserting one.
  - Locked by a different user: their name and last-marked-open time, with the choice framed as one of the two people potentially losing work if they choose Open over Open Read-Only.
- Read-Only scope is shallow, matching Word/Excel: Save is disabled outright; every other tab behaves exactly as normal, so edits made in a read-only session are genuinely lost if not saved — no read-only enforcement anywhere else in the app.
- Save As remains available in Read-Only and is the only way out of it. It now requires a folder different from the original workfile's folder (validated by comparing `os.path.dirname`, not by filename) — the actual reason is avoiding `outputs/pptx`/`outputs/pdf` collisions between two independent workfiles sharing a folder, not `.cgw` overwrite (which was already prevented for the exact-path case). On successful Save As, `read_only` flips to `False`, the lock is written at the new path, and the session becomes a normal editable one from that point — same pattern as Word/Excel "Save As while read-only".
- A persistent red **READ-ONLY** label sits next to the "ChartGen" heading in the main body for the whole session (visible on every tab, since it renders above the tab bar) — describes the file's current behaviour, not its history, so it carries no name/timestamp detail; that was already shown once on the decision screen at open.
- In a read-only session, Close Without Saving and Sign Out both proceed immediately with no confirmation dialog, even with unsaved edits — closing is treated as a deliberate decision, not one to second-guess.
- Explored but deliberately not built this session: a `beforeunload` browser warning on tab close (still worth doing, unrelated to the lock, catches the "forgot to save" case that concurrency work doesn't touch), a Save-changes prompt at explicit close for read-only sessions (rejected — inconsistent with the decision above not to second-guess Close/Sign Out), and any autosave/checkpoint mechanism (not raised again this session).

**Documentation:** Not yet updated. Message wording used in the decision screen and warnings is expected to change before this is finalised, so Architecture, Functional Spec, Feature List, and Refactoring Issues have deliberately been left untouched this session rather than documenting copy that's likely to be rewritten. This is the one open item carried into next session — see Next_Session.md.

**Git:** Repository on `C:\mcp_projects\ChartGen_PreFactor`. This session's work is committed as part of this close-down.

## Planned session breakdown (ChartGen_PreFactor scope)

| Session | Focus | Status |
|---|---|---|
| 1 | Quick wins — dead code + doc-only fixes | **Complete** |
| 2 | Workfile rename | **Complete** |
| 3 | Remaining terminology renames | **Complete** |
| 4 | Population stacking & explicit-value tokens | **Complete** |
| 5 | PopulationShape redesign | **Complete** |
| 6 | Concurrency review | Code complete; documentation write-up outstanding (see Next_Session.md) |
| 7 | Peer group / reference data | Not started — scope now narrower: only `organisations.csv` storage remains; binary peer group review logic was removed as a non-issue (see Session 4). |
| 8 | Placeholder simplification | Not started |
| 9 | Strip module numbering from code_base | Not started |
| 10 | Docstring protocol and review | **Complete** (resequenced ahead of Session 3) |

Items passed to the main refactor (not in this project's scope): type coercion at the CSV/WorkfileState boundary (two known instances — `enabled` and `unit_id` — plus `organisation_id` flagged as a further unaddressed one), whether untyped dict/row contracts should become typed structures, multi-project/multi-database support, `.cgw` file association and installer, Text Engine/Batch Controller module split, modular structure discussion (incl. nested sub-packages such as `chart_engine/tweaks/`, and `m15_insertions`), finding a permanent home for `constants_temp`, and a full content review of `app.py`. `base_charts.py`'s dead `_layer_colour` function and its lack of any other tweak/architecture work remain out of scope until a dedicated session.
