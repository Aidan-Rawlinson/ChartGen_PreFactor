"""
constants_temp.py
Column-order constants for the submissions and organisations reference tables.
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
