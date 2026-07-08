<!-- Purpose: Claude's handoff note -- what to pick up, open questions, and suggested first steps for the next session. Written by Claude at session end. -->

## Suggested first step

Part 1 is fully complete. Part 2 (main refactor) has begun opportunistically — one item pulled forward and resolved (type coercion), three stale items pruned. Next session should either:
- Continue scoping/resolving further Part 2 items as they come up, or
- Address any new issues the user raises.

No specific next session is pre-planned.

## Open questions for the user

None outstanding.

## Notes for continuity

- `constants_temp.py` now holds `FIELD_TYPES` and `coerce_row()` in addition to `UNITS_FIELDNAMES` — it remains a stopgap module without a permanent home (Part 2 item), and now has an additional reason to need one.
- The type-coercion fix touched `constants_temp.py`, `api_client.py`, `app.py`, `assembly_engine.py`, `workfile_file.py`, and `running_order.py`. `organisation_id`/`submission_id` are coerced to string at the API boundary (`get_submissions`/`get_organisations`); `enabled` coercion is now table-driven in both the `.cgw` open path and the `.xlsx` upload path. Untyped dicts vs. dataclasses (the related, larger Part 2 item) is untouched — deliberately kept separate.
- Module folder names are now: `data_acquisition`, `template_reader`, `running_order`, `data_shapes`, `chart_engine`, `assembly_engine`, `insert_picture`, `insert_from_excel`, `static_config`, `local_config`, `workfile_file`, plus `constants_temp`. Don't reintroduce `mNN_` naming anywhere.
- `Refactoring_issues_known.md` still refers to modules by their old `mNN_` names throughout in Part 1 (deliberate, historical record) — should not be changed to match current code.
- All other continuity notes from prior sessions (organisations.csv removal, placeholder type-based recognition, population resolution model, docstring protocol, etc.) still apply — see Progression_Log/Decisions for detail.
