"""
constants_temp.py
Temporary holding module for structural constants that don't yet have a
proper home.

SUBMISSIONS_FIELDNAMES and ORGANISATIONS_FIELDNAMES define the canonical
column order for the submissions and organisations reference tables — used
when serialising WorkfileState to CSV inside the .cgw (m14_workfile_file), and
when shaping the raw API response into organisation rows at New Workfile time
(app.py).

TEMPORARY — to be resolved in the main refactor. These constants describe
what a Submission/Organisation record looks like; they aren't owned by
persistence (m14) or by workfile setup (app.py), both of which are just
consumers. Likely destination: a definitions-only module, once
m04_data_shapes is split into pure data structures versus the filter/recalc
operations that currently live there alongside them. See Refactoring Issues,
Part 2.
"""

SUBMISSIONS_FIELDNAMES = [
    "submission_id",
    "submission_code",
    "submission_name",
    "submission_year",
    "project_id",
    "project_name",
    "organisation_id",
    "organisation_name",
    "submission_service_count",
    "response_count",
    "submission_level",
    "service_item_ids",
    "service_item_names",
    "service_response_counts",
    "Region()",
]

ORGANISATIONS_FIELDNAMES = [
    "organisation_id",
    "organisation_name",
    "nhs_code",
    "organisation_type_name",
    "region_name",
]
