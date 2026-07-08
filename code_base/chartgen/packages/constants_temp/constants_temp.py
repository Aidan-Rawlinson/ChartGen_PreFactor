"""
constants_temp.py
Shared record-shape constants and CSV/WorkfileState field-type coercion.
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


FIELD_TYPES = {
    "submission_id":   str,
    "unit_id":         str,
    "organisation_id": str,
    "enabled":         "bool_int",
}


def coerce_row(row: dict, field_types: dict = FIELD_TYPES) -> dict:
    """Coerce known fields in a dict to their canonical type in place; fields not present are left untouched."""
    for field, target in field_types.items():
        if field not in row:
            continue
        value = row[field]
        if target is str:
            row[field] = "" if value is None else str(value)
        elif target == "bool_int":
            row[field] = 1 if str(value).strip() in ("1", "True", "true", "yes") else 0
    return row
