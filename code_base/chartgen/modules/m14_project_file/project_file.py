"""
project_file.py
M14 — Project File: .cgp file format and ProjectState management.

Owns everything to do with the .cgp ZIP archive:
  - ProjectState dataclass — in-memory representation of all project data
  - open_project   — read .cgp into ProjectState
  - save_project   — serialise ProjectState back to .cgp
  - new_project    — create a blank ProjectState
  - close_project  — clear lock fields and discard state

No other module touches the ZIP directly. Everything else in the codebase
receives a ProjectState and works against it.

Lock mechanism:
  project_info.json inside the .cgp carries locked_by / locked_at fields.
  These are written on open (after login) and cleared on close.
  A second user opening a locked project sees an advisory warning before
  proceeding to login. The lock is advisory — stale locks from crashes are
  handled by the warning prompt, not by a hard block.
"""

import io
import json
import zipfile
import csv
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


CHARTGEN_VERSION = "0.1-prototype"


@dataclass
class ProjectState:
    """
    In-memory representation of everything inside a .cgp file.
    Loaded from ZIP at open; serialised back to ZIP on save.
    """
    # File identity
    cgp_path: str = ""                  # absolute path to .cgp on disk
    project_name: str = ""

    # project_config/
    settings: dict = field(default_factory=dict)
    urls: list = field(default_factory=list)          # list of {url, label}
    submissions: list = field(default_factory=list)   # list of dicts
    organisations: list = field(default_factory=list) # list of dicts
    running_order_rows: list = field(default_factory=list)  # list of dicts (CSV rows)

    # data_cache/
    manifest: dict = field(default_factory=dict)      # keyed by tier_group_option key
    cache: dict = field(default_factory=dict)         # keyed by filename -> json string

    # template/
    template_pptx_bytes: Optional[bytes] = None       # reference copy bytes

    # project_info.json
    last_saved_by: str = ""
    last_saved_at: str = ""
    locked_by: str = ""
    locked_at: str = ""

    # Session state — not persisted
    dirty: bool = False


# ---------------------------------------------------------------------------
# Internal CSV helpers
# ---------------------------------------------------------------------------

def _csv_to_rows(text: str) -> list:
    """Parse CSV text into a list of dicts."""
    reader = csv.DictReader(io.StringIO(text))
    return list(reader)


def _rows_to_csv(rows: list, fieldnames: list = None) -> str:
    """Serialise a list of dicts to CSV text."""
    if not rows and not fieldnames:
        return ""
    out = io.StringIO()
    fn = fieldnames or list(rows[0].keys())
    writer = csv.DictWriter(out, fieldnames=fn)
    writer.writeheader()
    writer.writerows(rows)
    return out.getvalue()


def _key_value_csv_to_dict(text: str) -> dict:
    """Parse a key/value CSV (key,value header) into a dict."""
    reader = csv.DictReader(io.StringIO(text))
    return {row["key"]: row["value"].strip() for row in reader}


def _dict_to_key_value_csv(d: dict) -> str:
    """Serialise a dict to key/value CSV."""
    out = io.StringIO()
    writer = csv.DictWriter(out, fieldnames=["key", "value"])
    writer.writeheader()
    for k, v in d.items():
        writer.writerow({"key": k, "value": v})
    return out.getvalue()


def _url_csv_to_list(text: str) -> list:
    """Parse urls.csv (url,label, no header) into list of dicts."""
    rows = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split(",", 1)
        rows.append({"url": parts[0].strip(), "label": parts[1].strip() if len(parts) > 1 else ""})
    return rows


def _url_list_to_csv(urls: list) -> str:
    """Serialise url list back to urls.csv format (no header)."""
    return "\n".join(f"{u['url']},{u.get('label','')}" for u in urls)


# ---------------------------------------------------------------------------
# Read project_info.json from ZIP without full extraction
# ---------------------------------------------------------------------------

def read_project_info(cgp_path: str) -> dict:
    """
    Read project_info.json from a .cgp without loading the full archive.
    Returns empty dict if file does not exist or cannot be read.
    """
    try:
        with zipfile.ZipFile(cgp_path, "r") as zf:
            if "project_info.json" in zf.namelist():
                return json.loads(zf.read("project_info.json").decode("utf-8"))
    except Exception:
        pass
    return {}


# ---------------------------------------------------------------------------
# Open
# ---------------------------------------------------------------------------

def open_project(cgp_path: str) -> ProjectState:
    """
    Load a .cgp into a ProjectState.
    Does NOT write lock fields — caller writes lock after successful login.
    """
    state = ProjectState(cgp_path=cgp_path)

    with zipfile.ZipFile(cgp_path, "r") as zf:
        names = zf.namelist()

        def _read(name):
            return zf.read(name).decode("utf-8") if name in names else ""

        def _read_bytes(name):
            return zf.read(name) if name in names else None

        # project_config/
        state.settings         = _key_value_csv_to_dict(_read("project_config/settings.csv"))
        state.urls             = _url_csv_to_list(_read("project_config/urls.csv"))
        state.submissions      = _csv_to_rows(_read("project_config/submissions.csv"))
        state.organisations    = _csv_to_rows(_read("project_config/organisations.csv"))
        state.running_order_rows = _csv_to_rows(_read("project_config/running_order.csv"))
        for _row in state.running_order_rows:
            _row["enabled"] = 1 if str(_row.get("enabled", "1")).strip() in ("1", "True", "true", "yes") else 0

        # data_cache/
        if "data_cache/manifest.json" in names:
            state.manifest = json.loads(zf.read("data_cache/manifest.json").decode("utf-8"))
        for name in names:
            if name.startswith("data_cache/") and name.endswith(".json") and name != "data_cache/manifest.json":
                fname = name.split("/")[-1]
                state.cache[fname] = zf.read(name).decode("utf-8")

        # template/
        for name in names:
            if name.startswith("template/") and name.endswith(".pptx"):
                state.template_pptx_bytes = _read_bytes(name)
                break

        # project_info.json
        if "project_info.json" in names:
            info = json.loads(zf.read("project_info.json").decode("utf-8"))
            state.project_name   = info.get("project_name", "")
            state.last_saved_by  = info.get("last_saved_by", "")
            state.last_saved_at  = info.get("last_saved_at", "")
            state.locked_by      = info.get("locked_by", "")
            state.locked_at      = info.get("locked_at", "")

    state.dirty = False
    return state


def write_lock(cgp_path: str, username: str):
    """
    Write locked_by / locked_at into project_info.json inside the .cgp.
    Called after successful login.
    """
    _update_project_info(cgp_path, {
        "locked_by": username,
        "locked_at": datetime.now(timezone.utc).isoformat(),
    })


def clear_lock(cgp_path: str):
    """
    Clear locked_by / locked_at from project_info.json inside the .cgp.
    Called on any close route.
    """
    _update_project_info(cgp_path, {
        "locked_by": "",
        "locked_at": "",
    })


def _update_project_info(cgp_path: str, updates: dict):
    """
    Read project_info.json from .cgp, apply updates, write back.
    Uses a full rewrite of the ZIP to update the uncompressed entry cleanly.
    """
    try:
        info = read_project_info(cgp_path)
        info.update(updates)
        _rewrite_single_file(cgp_path, "project_info.json",
                             json.dumps(info, indent=2).encode("utf-8"),
                             compress_type=zipfile.ZIP_STORED)
    except Exception:
        pass


def _rewrite_single_file(cgp_path: str, arcname: str, data: bytes, compress_type=zipfile.ZIP_DEFLATED):
    """
    Replace a single file inside a ZIP by rewriting the full archive.
    This avoids duplicate entries that zipfile append mode creates.
    """
    buf = io.BytesIO()
    with zipfile.ZipFile(cgp_path, "r") as zin:
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                if item.filename == arcname:
                    zout.writestr(zipfile.ZipInfo(arcname), data)
                    # set compression on the ZipInfo
                    zout.NameToInfo[arcname].compress_type = compress_type
                else:
                    zout.writestr(item, zin.read(item.filename))
            if arcname not in [i.filename for i in zin.infolist()]:
                info = zipfile.ZipInfo(arcname)
                info.compress_type = compress_type
                zout.writestr(info, data)
    with open(cgp_path, "wb") as f:
        f.write(buf.getvalue())


# ---------------------------------------------------------------------------
# Save
# ---------------------------------------------------------------------------

def save_project(state: ProjectState, username: str, target_path: str = None):
    """
    Serialise ProjectState back to the .cgp ZIP.
    Updates last_saved_by / last_saved_at. Does not touch lock fields.

    target_path: write to this path instead of state.cgp_path, and update
    state.cgp_path to match (used by Save As). Defaults to state.cgp_path.
    """
    from modules.m10_project_config.submissions import FIELDNAMES as SUB_FIELDS
    from modules.m10_project_config.organisations import FIELDNAMES as ORG_FIELDS

    now = datetime.now(timezone.utc).isoformat()
    state.last_saved_by = username
    state.last_saved_at = now

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:

        def _write(arcname, text):
            zf.writestr(arcname, text.encode("utf-8"))

        # project_config/
        _write("project_config/settings.csv",      _dict_to_key_value_csv(state.settings))
        _write("project_config/urls.csv",           _url_list_to_csv(state.urls))
        _write("project_config/submissions.csv",
               _rows_to_csv(state.submissions, SUB_FIELDS) if state.submissions else "")
        _write("project_config/organisations.csv",
               _rows_to_csv(state.organisations, ORG_FIELDS) if state.organisations else "")

        # running_order — derive fieldnames from rows if present
        if state.running_order_rows:
            from modules.m03_running_order.running_order import COLUMNS
            _write("project_config/running_order.csv",
                   _rows_to_csv(state.running_order_rows, COLUMNS))
        else:
            _write("project_config/running_order.csv", "")

        # data_cache/
        _write("data_cache/manifest.json", json.dumps(state.manifest, indent=2))
        for fname, json_str in state.cache.items():
            zf.writestr(f"data_cache/{fname}", json_str.encode("utf-8"))

        # template/
        if state.template_pptx_bytes:
            project_name = state.project_name or "template"
            zf.writestr(f"template/{project_name}.pptx", state.template_pptx_bytes)

        # project_info.json — uncompressed
        info = {
            "project_name":      state.project_name,
            "last_saved_by":     state.last_saved_by,
            "last_saved_at":     state.last_saved_at,
            "chartgen_version":  CHARTGEN_VERSION,
            "locked_by":         state.locked_by,
            "locked_at":         state.locked_at,
        }
        zi = zipfile.ZipInfo("project_info.json")
        zi.compress_type = zipfile.ZIP_STORED
        zf.writestr(zi, json.dumps(info, indent=2).encode("utf-8"))

    save_path = target_path or state.cgp_path
    with open(save_path, "wb") as f:
        f.write(buf.getvalue())

    state.cgp_path = save_path
    state.dirty = False


# ---------------------------------------------------------------------------
# New
# ---------------------------------------------------------------------------

def new_project(cgp_path: str, project_name: str) -> ProjectState:
    """
    Create a blank ProjectState and write an empty .cgp to disk.
    Caller populates settings / submissions / etc. before first save.
    """
    state = ProjectState(
        cgp_path=cgp_path,
        project_name=project_name,
        dirty=True,
    )
    # Write a minimal .cgp immediately so the file exists on disk
    _write_empty_cgp(cgp_path, project_name)
    return state


def _write_empty_cgp(cgp_path: str, project_name: str):
    os.makedirs(os.path.dirname(cgp_path), exist_ok=True) if os.path.dirname(cgp_path) else None
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for name in [
            "project_config/settings.csv",
            "project_config/urls.csv",
            "project_config/submissions.csv",
            "project_config/organisations.csv",
            "project_config/running_order.csv",
            "data_cache/manifest.json",
        ]:
            zf.writestr(name, b"")
        # empty manifest
        zf.writestr("data_cache/manifest.json", json.dumps({}).encode("utf-8"))
        # project_info
        info = {
            "project_name":     project_name,
            "last_saved_by":    "",
            "last_saved_at":    "",
            "chartgen_version": CHARTGEN_VERSION,
            "locked_by":        "",
            "locked_at":        "",
        }
        zi = zipfile.ZipInfo("project_info.json")
        zi.compress_type = zipfile.ZIP_STORED
        zf.writestr(zi, json.dumps(info, indent=2).encode("utf-8"))
    with open(cgp_path, "wb") as f:
        f.write(buf.getvalue())


# ---------------------------------------------------------------------------
# Close
# ---------------------------------------------------------------------------

def close_project(state: ProjectState):
    """
    Clear lock fields in the .cgp and discard the ProjectState.
    Called on both Save and Close and Close Without Saving routes.
    """
    if state.cgp_path and os.path.exists(state.cgp_path):
        clear_lock(state.cgp_path)
