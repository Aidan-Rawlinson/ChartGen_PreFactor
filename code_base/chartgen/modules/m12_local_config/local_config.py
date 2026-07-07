"""
local_config.py
Per-machine, per-user configuration (credentials) and per-batch runtime context (ReportContext).
"""

import os
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ReportContext:
    """
    Runtime context for a single report in a batch run.
    Constructed by the Assembly Engine; passed to render_chart.
    """
    unit_id:            str
    unit_code:          str
    unit_name:          str
    organisation_id:    str
    organisation_name:  str


def get_peer_group_columns(units: list) -> list:
    """
    Return peer group column names (matching the Name() pattern) from the unit table, in column order.
    Does not include 'All' or 'Selected' — callers add those.
    """
    if not units:
        return []
    return [col for col in units[0].keys() if col.endswith("()")]


def get_peer_group_value_options(units: list) -> list:
    """
    Return populations-string tokens for every peer group column, in column order.
    For each Name() column, yields the bare token first, then one Name(Value) token
    per distinct value present in that column, sorted alphabetically, excluding
    blank and 'x' (both mean the unit has no group for that column).
    Does not include 'All' or 'Selected' — callers add those.
    """
    if not units:
        return []
    options = []
    for col in get_peer_group_columns(units):
        name = col[:-2]  # strip trailing "()"
        options.append(col)
        values = sorted({
            (r.get(col) or "").strip() for r in units
            if (r.get(col) or "").strip() and (r.get(col) or "").strip() != "x"
        })
        options.extend(f"{name}({v})" for v in values)
    return options


def build_report_context(settings: dict, units: list) -> Optional[ReportContext]:
    """
    Build a ReportContext from settings and the loaded unit list.
    Returns None if no unit is selected or the selected ID is not found.
    """
    selected_id = str(settings.get("selected_unit_id", "") or "").strip()
    if not selected_id:
        return None

    row = next((r for r in units if str(r["unit_id"]) == selected_id), None)
    if row is None:
        return None

    return ReportContext(
        unit_id=str(row["unit_id"]),
        unit_code=row["unit_code"],
        unit_name=row["unit_name"],
        organisation_id=row["organisation_id"],
        organisation_name=row["organisation_name"],
    )


import csv as _csv_mod

# ---------------------------------------------------------------------------
# Credentials — stored locally, never in the workfile
# ---------------------------------------------------------------------------

_CREDENTIALS_PATH = os.path.join(os.path.dirname(__file__), "credentials.csv")


def get_credentials_path() -> str:
    return _CREDENTIALS_PATH


def load_last_username() -> str:
    """Return the last successfully authenticated username, or empty string."""
    if not os.path.exists(_CREDENTIALS_PATH):
        return ""
    with open(_CREDENTIALS_PATH, newline="", encoding="utf-8-sig") as f:
        reader = _csv_mod.DictReader(f)
        row = next(reader, None)
        if row is None:
            return ""
        return row.get("username", "").strip()


def save_last_username(username: str):
    """Persist the username only — no password stored."""
    with open(_CREDENTIALS_PATH, "w", newline="", encoding="utf-8") as f:
        writer = _csv_mod.DictWriter(f, fieldnames=["username"])
        writer.writeheader()
        writer.writerow({"username": username})
