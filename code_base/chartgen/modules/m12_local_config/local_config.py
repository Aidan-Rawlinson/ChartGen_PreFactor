"""
local_config.py
M12 — Local Config: per-machine, per-user configuration and runtime context.

Owns two distinct concerns:
  1. Local user config — credentials and anything else that is per-user /
     per-machine rather than per-project. This data must NOT live in the
     project file (which is shareable) or in static config. Credentials
     storage here is a temporary arrangement pending a full credentials
     model redesign.

  2. Runtime context — ReportContext holds the selected reporting unit and
     any population context needed by the chart engine for highlighting.
     It is constructed once per batch run by the Assembly Engine from
     settings and the submissions CSV, then passed through the pipeline
     to every render_chart call.

Future additions (peer groups, hierarchy level) slot in cleanly here
without touching the data layer or the config layer.

NOTE — PopulationSlice and resolve_populations were removed in Stage 10.
They were an early sketch of the populations model, superseded by:
  - PopulationShape  in m04_data_shapes/shapes.py
  - build_population_shapes  in m06_assembly_engine/assembly_engine.py
Those are the live implementations. This module owns only ReportContext
and the helpers that construct it.
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
    submission_id:      int
    submission_code:    str
    submission_name:    str
    organisation_id:    str
    organisation_name:  str


def get_peer_group_columns(submissions: list) -> list:
    """
    Return peer group column names from the submissions CSV, in column order.
    These are columns whose names match the Name() pattern.
    Bookended options (All, Selected) are not included — callers add those.
    """
    if not submissions:
        return []
    return [col for col in submissions[0].keys() if col.endswith("()")]


def build_report_context(settings: dict, submissions: list) -> Optional[ReportContext]:
    """
    Build a ReportContext from settings and the loaded submissions list.
    Returns None if no submission is selected or the selected ID is not found.
    """
    selected_id = str(settings.get("selected_submission_id", "") or "").strip()
    if not selected_id:
        return None

    row = next((r for r in submissions if str(r["submission_id"]) == selected_id), None)
    if row is None:
        return None

    return ReportContext(
        submission_id=int(row["submission_id"]),
        submission_code=row["submission_code"],
        submission_name=row["submission_name"],
        organisation_id=row["organisation_id"],
        organisation_name=row["organisation_name"],
    )


import csv as _csv_mod

# ---------------------------------------------------------------------------
# Credentials — stored locally, never in the project file
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
