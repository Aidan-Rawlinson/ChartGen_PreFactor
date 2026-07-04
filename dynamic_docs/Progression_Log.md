<!-- Purpose: A session-by-session history of what was built and what was decided. The project record. Authored by Claude at session level, not micro-decision level. -->

## Session 1 — [Date not specified] — Project onboarding and pre-refactor planning

Set up Git on the project folder (init, remote, initial commit and push). Reviewed the previously-empty `code_base` folder once the user populated it with the vibe-coded proof-of-concept (`chartgen/` — `app.py`, 12 numbered modules, config, and support files); confirmed structure against the Architecture document's module map without reading code contents. Reviewed all seven product documents (Primer, Architecture, Functional Spec, Feature List, Glossary, Refactoring Issues, Docs Maintenance Guide) and confirmed the `static_docs_mirror/project_files` mirror matched Project Files.

Reviewed and categorised the pre-existing Refactoring Issues log (24 items) into: items for this project (ChartGen_PreFactor) versus items to pass forward to the main refactor, then further split the "this project" items into 9 focused sessions. Iterated on the split with the user — moved `organisations.csv` storage, binary peer group logic, and explicit-value peer group tokens into this project's scope; clarified "review placeholder logic" as PowerPoint placeholder simplification/documentation; split module-numbering removal from the codebase into its own standalone session (9) given unknown import blast radius, separate from the doc-only module-numbering fix (Session 1).

Rewrote `Refactoring_issues_known.md` into the new two-part structure (Part 1: this project, by session; Part 2: main refactor) preserving all original item text. Approved and written to the mirror.
