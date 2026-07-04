"""
submissions.py
M10 — Project Config: submissions table helpers.

Writes and reads submissions.csv — the primary item table for the project.
One row per submission. Service lists stored as pipe-delimited strings in
three columns (service_item_ids, service_item_names, service_response_counts).
"""

import os
import csv

from modules.m10_project_config.organisations import get_organisation_lookup

SUBMISSIONS_PATH = os.path.join(os.path.dirname(__file__), "submissions.csv")

FIELDNAMES = [
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


def save_submissions(rows: list, path: str = SUBMISSIONS_PATH):
    """
    Write submission rows (as returned by api_client.get_submissions) to CSV.
    Service lists are flattened to pipe-delimited strings.
    Region() is resolved from organisations.csv via organisation_id and written
    permanently — the join happens once at save time.
    """
    org_lookup = get_organisation_lookup()
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        for row in rows:
            services = row.get("services", [])
            org = org_lookup.get(str(row["organisation_id"]), {})
            writer.writerow({
                "submission_id":            row["submission_id"],
                "submission_code":          row["submission_code"],
                "submission_name":          row["submission_name"],
                "submission_year":          row["submission_year"],
                "project_id":               row["project_id"],
                "project_name":             row["project_name"],
                "organisation_id":          row["organisation_id"],
                "organisation_name":        row["organisation_name"],
                "submission_service_count": row["submission_service_count"],
                "response_count":           row["response_count"],
                "submission_level":         row["submission_level"],
                "service_item_ids":   "|".join(str(s["service_item_id"])   for s in services),
                "service_item_names": "|".join(str(s["service_item_name"]) for s in services),
                "service_response_counts": "|".join(str(s["response_count"]) for s in services),
                "Region()":                org.get("region_name", ""),
            })


def load_submissions(path: str = SUBMISSIONS_PATH) -> list:
    """
    Load submissions from CSV. Returns list of dicts matching FIELDNAMES.
    Returns empty list if file does not exist.
    """
    if not os.path.exists(path):
        return []
    with open(path, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def submissions_to_display_rows(rows: list, expand_services: bool = False) -> list:
    """
    Prepare submission rows for display in the Populations table.

    expand_services=False: one row per submission, service columns as pipe-delimited strings.
    expand_services=True:  one row per service for submissions that have services;
                           submissions without services appear as a single row with blank service columns.
                           Submission-level columns repeat on every service row.
    """
    if not expand_services:
        return rows

    expanded = []
    for row in rows:
        ids   = [v for v in row["service_item_ids"].split("|")          if v] if row["service_item_ids"] else []
        names = [v for v in row["service_item_names"].split("|")        if v] if row["service_item_names"] else []
        counts= [v for v in row["service_response_counts"].split("|")   if v] if row["service_response_counts"] else []

        if not ids:
            expanded.append(row)
        else:
            for i, sid in enumerate(ids):
                expanded.append({
                    **row,
                    "service_item_ids":          sid,
                    "service_item_names":         names[i] if i < len(names) else "",
                    "service_response_counts":    counts[i] if i < len(counts) else "",
                })
    return expanded
