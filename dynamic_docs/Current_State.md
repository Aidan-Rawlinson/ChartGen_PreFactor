<!-- Purpose: A snapshot of where the project stands right now -- what works, what is in progress, what is broken. Rewritten by Claude each session. -->

## Status: Part 1 remains fully complete (Sessions 1–10). This session worked on Part 2 (main refactor) items — one pruned, one pulled forward and implemented as an agreed exception.

**Refactoring Issues log pruned.** Three Part 2 items removed at user request as no longer worth tracking: the `beforeunload` browser warning, autosave/checkpoint mechanisms, and the advisory-lock re-check-at-Save gap.

**Type coercion (Part 2 item) pulled into pre-factor and resolved.** Normally structural Part 2 items stay deferred to the main refactor, but this one was explicitly pulled forward as a one-off exception. Implemented as a shared `FIELD_TYPES` table plus a single `coerce_row()` function in `constants_temp.py` — not typed dataclasses, which remains a separate, larger Part 2 question. Changes:
- `api_client.py`'s `get_submissions()`/`get_organisations()` now coerce every returned row, so `organisation_id` (and `submission_id`) become strings at their true point of origin — the same treatment `submission_id` already had from Session 4, now table-driven instead of a bespoke ternary.
- The two ad hoc `enabled` truthy-parsers (`workfile_file.py` on `.cgw` open, `running_order.py` on `.xlsx` upload) both now call the shared function.
- Four now-redundant defensive `str()` wraps around `organisation_id` comparisons removed from `app.py` and `assembly_engine.py`.
- `Refactoring_issues_known.md` Part 2 entry marked Done in place (strikethrough retained), noting it was a pre-factor exception rather than a Part 1 session.

## Planned session breakdown (ChartGen_PreFactor scope)

| Session | Focus | Status |
|---|---|---|
| 1–10 | (see prior entries) | **Complete** |

Part 1 is fully complete. Remaining work is Part 2 items, deferred to the main refactor except where explicitly pulled forward (as above) — see `Refactoring_issues_known.md`.

**Git:** Not committed yet this session — close-down commit pending. Note: the previous session's close-down also shows an unclear result — `git_log.txt` records a `[FAILED]` on `git commit` immediately followed by an `[OK]` on `git push`, from 2026-07-08 14:29. Per standing practice this tool's failure report isn't always reliable; verify actual repository state independently if it matters before relying on history from that point.
