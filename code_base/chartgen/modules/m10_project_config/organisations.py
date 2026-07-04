"""
organisations.py
M10 — Project Config: organisation reference table helpers.

Writes and reads organisations.csv — the organisation reference list fetched from
the API before the submissions table is created or updated. Used to resolve
organisation_id to region and type for peer group assignment.
"""

import os
import csv

ORGANISATIONS_PATH = os.path.join(os.path.dirname(__file__), "organisations.csv")

FIELDNAMES = [
    "organisation_id",
    "organisation_name",
    "nhs_code",
    "organisation_type_name",
    "region_name",
]


def save_organisations(rows: list, path: str = ORGANISATIONS_PATH):
    """
    Write organisation rows (as returned by api_client.get_organisations) to CSV.
    """
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        for row in rows:
            writer.writerow({
                "organisation_id":        row["organisation_id"],
                "organisation_name":      row["organisation_name"],
                "nhs_code":               row["nhs_code"],
                "organisation_type_name": row["organisation_type_name"],
                "region_name":            row["region_name"],
            })


def load_organisations(path: str = ORGANISATIONS_PATH) -> list:
    """
    Load organisations from CSV. Returns list of dicts matching FIELDNAMES.
    Returns empty list if file does not exist.
    """
    if not os.path.exists(path):
        return []
    with open(path, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def get_organisation_lookup(path: str = ORGANISATIONS_PATH) -> dict:
    """
    Returns a dict keyed by organisation_id (str) for fast lookup.
    """
    return {row["organisation_id"]: row for row in load_organisations(path)}
