<!-- Purpose: A snapshot of where the project stands right now -- what works, what is in progress, what is broken. Rewritten by Claude each session. -->

## Status: In Progress — Session 4 complete (Refactoring Issues Session 10, resequenced ahead of Session 3)

**Codebase:** `code_base/chartgen/` — Refactoring Issues Session 10 (Docstring protocol and review) is done, executed ahead of Session 3 at the user's request. A docstring protocol was agreed: a docstring states only identity — what a module/function is or does — never mechanics, rationale, design intent, roadmap language, or cross-references to other documents or constants. Length target is 1 sentence, 2 with strong justification. One deliberate exception: untyped dict/row contracts with no type defined elsewhere (API response shapes, Running Order row fields, yellow-box classification, the populations-string token legend) are kept in docstrings since cutting them loses information with no other home. Dataclass field-position/semantics documentation (e.g. `values[i]` correspondence, `PopulationShape.role` string-value meaning) did **not** get the same exception and was cut. Every module and function docstring across all 17 files in `code_base/chartgen/` (`app.py` plus every module under `modules/`, excluding `chart_type_map.py` which was already compliant) was reviewed and rewritten to this policy — no logic changes, docstrings only. This reverses the Session 1 `running_order.py` docstring pattern, which had cross-referenced Architecture/Functional Spec; that is no longer the approach. One disputed factual claim in `running_order.py`'s `read_xlsx` docstring (whether it actually skips `enabled == 0` rows) was raised and, per the user's instruction, left untouched with no special handling.

**Documentation:** `Refactoring_issues_known.md` is the only one of the seven reference documents that changed this session — Session 10 marked done with the policy writeup, and a new Part 2 item added on whether untyped dict/row structures should become typed (dataclasses/TypedDicts) for accountability, given the vibe-coded origin of the codebase. Written to the mirror. Primer, Architecture, Functional Spec, Feature List, Glossary, and the Docs Maintenance Guide were not touched this session.

**Git:** Repository initialised on `C:\mcp_projects\ChartGen_PreFactor`, remote linked, initial commit and push completed. Sessions 1–3 (Progression_Log numbering) work has since been committed in prior close-downs; this session's work (Progression_Log Session 4) is committed as part of this close-down.

## Planned session breakdown (ChartGen_PreFactor scope)

| Session | Focus | Status |
|---|---|---|
| 1 | Quick wins — dead code + doc-only fixes | **Complete** |
| 2 | Workfile rename | **Complete** |
| 3 | Remaining terminology renames | Not started |
| 4 | Population stacking & explicit-value tokens | Not started |
| 5 | PopulationShape redesign | Not started |
| 6 | Concurrency review | Not started |
| 7 | Peer group / reference data | Not started |
| 8 | Placeholder simplification | Not started |
| 9 | Strip module numbering from code_base | Not started |
| 10 | Docstring protocol and review | **Complete** (resequenced ahead of Session 3) |

Items passed to the main refactor (not in this project's scope): type coercion at the CSV/WorkfileState boundary, whether untyped dict/row contracts should become typed structures (new this session), multi-project/multi-database support, `.cgw` file association and installer, Text Engine/Batch Controller module split, modular structure discussion (incl. nested sub-packages such as `chart_engine/tweaks/`, and `m15_insertions`), finding a permanent home for `constants_temp`, and a full content review of `app.py`.
