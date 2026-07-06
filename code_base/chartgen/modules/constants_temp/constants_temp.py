"""
constants_temp.py
Column-order constants for the units and organisations reference tables.
"""

UNITS_FIELDNAMES = [
    "unit_id",
    "unit_code",
    "unit_name",
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
