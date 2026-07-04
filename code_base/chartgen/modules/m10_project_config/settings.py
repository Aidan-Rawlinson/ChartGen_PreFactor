"""
settings.py
M10 — Project Config: settings helpers

Reads and writes settings.csv (key/value store for project-level configuration).
"""

import os
import csv

SETTINGS_PATH = os.path.join(os.path.dirname(__file__), "settings.csv")


def load_settings() -> dict:
    if not os.path.exists(SETTINGS_PATH):
        return {}
    with open(SETTINGS_PATH, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        return {row["key"]: row["value"].strip() for row in reader}


def save_settings(settings: dict):
    with open(SETTINGS_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["key", "value"])
        writer.writeheader()
        for key, value in settings.items():
            writer.writerow({"key": key, "value": value})


def get_output_folder(settings: dict) -> str:
    project_folder = settings.get("project_folder", "").strip()
    output_folder = os.path.join(project_folder, "outputs") if project_folder else "outputs"
    os.makedirs(output_folder, exist_ok=True)
    return output_folder


def get_settings(project_state=None) -> dict:
    """Return settings from ProjectState if available, otherwise from disk."""
    if project_state is not None:
        return project_state.settings
    return load_settings()


def set_settings(settings: dict, project_state=None):
    """Write settings to ProjectState if available, otherwise to disk."""
    if project_state is not None:
        project_state.settings = settings
        project_state.dirty = True
    else:
        save_settings(settings)


def get_output_folder_from_state(project_state=None) -> str:
    """Derive output folder from ProjectState or disk settings."""
    settings = get_settings(project_state)
    cgp_path = project_state.cgp_path if project_state else ""
    if cgp_path:
        base = os.path.dirname(cgp_path)
    else:
        base = settings.get("project_folder", "").strip() or "."
    folder = os.path.join(base, "outputs")
    os.makedirs(folder, exist_ok=True)
    return folder
