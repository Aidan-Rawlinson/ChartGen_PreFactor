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
