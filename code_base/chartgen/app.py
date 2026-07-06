"""
app.py
ChartGen Python Prototype — Streamlit entry point.
"""

import os
import sys
import datetime

sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st

from modules.m01_data_acquisition.fetch import fetch_all
from modules.m01_data_acquisition.api_client import get_token
from modules.m05_chart_engine.cache_reader import list_cached_files, load_shape, load_manifest
from modules.m05_chart_engine.chart_type_map import get_valid_chart_types
from modules.m05_chart_engine.base_charts import render_chart
from modules.m12_local_config.local_config import load_last_username, save_last_username
from modules.m14_workfile_file.workfile_file import (
    WorkfileState, open_workfile, save_workfile, new_workfile, close_workfile,
    read_workfile_info, write_lock, clear_lock
)

CHART_TYPE_MAP_PATH = os.path.join(
    os.path.dirname(__file__), "modules", "m09_static_config", "chart_type_map.csv"
)
DEFAULT_EMAIL = "aidan.rawlinson@nhs.net"


# ---------------------------------------------------------------------------
# Helpers — WorkfileState accessors
# ---------------------------------------------------------------------------

def _format_uk_time(iso_str: str) -> str:
    """Convert a stored UTC ISO timestamp to UK local time (GMT/BST aware)."""
    if not iso_str:
        return ""
    try:
        from zoneinfo import ZoneInfo
        dt = datetime.datetime.fromisoformat(iso_str)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=datetime.timezone.utc)
        uk_dt = dt.astimezone(ZoneInfo("Europe/London"))
        return uk_dt.strftime("%Y-%m-%d %H:%M")
    except Exception:
        return iso_str[:16].replace("T", " ")


def _ws() -> WorkfileState:
    """Return the current WorkfileState from session state."""
    return st.session_state.get("workfile_state")


def _has_workfile() -> bool:
    return _ws() is not None


def _settings() -> dict:
    return _ws().settings


def _save_settings(s: dict):
    ws = _ws()
    ws.settings = s
    ws.dirty = True


def _submissions() -> list:
    return _ws().submissions


def _manifest() -> dict:
    ws = _ws()
    return load_manifest(ws)


def _cached_files() -> list:
    ws = _ws()
    return list_cached_files(ws)


def _load_shape_ps(filename):
    ws = _ws()
    return load_shape(filename, ws)


def _clear_workfile_session_state():
    for k in ["ro_rows", "ro_file_mtime", "ro_selected_idx", "run_log_rows",
              "pop_expander_open", "pop_expand_services_val", "pop_include_org_val"]:
        st.session_state.pop(k, None)


# ---------------------------------------------------------------------------
# Login
# ---------------------------------------------------------------------------

def show_login(lock_info: dict = None):
    st.set_page_config(page_title="ChartGen — Sign In", layout="centered")
    st.title("ChartGen")
    st.caption("Analysis and Reporting software")
    st.subheader("Sign in")

    if lock_info and lock_info.get("locked_by"):
        st.warning(
            f"This workfile was opened by **{lock_info['locked_by']}** "
            f"on {lock_info.get('locked_at', 'unknown time')}. "
            "Are you sure you want to open it?"
        )
        if st.button("Cancel — do not open"):
            st.session_state.pop("pending_workfile_path", None)
            st.rerun()

    default_email = load_last_username() or DEFAULT_EMAIL

    with st.form("login_form"):
        email = st.text_input("Email", value=default_email)
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Sign in")

    if submitted:
        if not email or not password:
            st.error("Please enter both email and password.")
        else:
            with st.spinner("Signing in…"):
                try:
                    token = get_token(email.strip(), password)
                    save_last_username(email.strip())
                    st.session_state["authenticated"] = True
                    st.session_state["username"] = email.strip()
                    st.session_state["token"] = token

                    # If we were opening a .cgw, write the lock and load it now
                    pending = st.session_state.pop("pending_workfile_path", None)
                    if pending:
                        write_lock(pending, email.strip())
                        ws = open_workfile(pending)
                        ws.locked_by = email.strip()
                        st.session_state["workfile_state"] = ws

                    st.rerun()
                except Exception as e:
                    st.error(f"Sign in failed — please check your credentials. ({e})")


# ---------------------------------------------------------------------------
# Auth gate
# ---------------------------------------------------------------------------

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    lock_info = None
    pending = st.session_state.get("pending_workfile_path")
    if pending and os.path.exists(pending):
        info = read_workfile_info(pending)
        if info.get("locked_by"):
            lock_info = info
    show_login(lock_info=lock_info)
    st.stop()


# ---------------------------------------------------------------------------
# Main app layout
# ---------------------------------------------------------------------------

st.set_page_config(page_title="ChartGen", layout="wide")

# ---------------------------------------------------------------------------
# Sidebar — file operations
# ---------------------------------------------------------------------------

with st.sidebar:
    st.markdown("## ChartGen")
    st.caption("Analysis and Reporting software")
    st.divider()

    ws = _ws()
    has_workfile = ws is not None

    if has_workfile:
        workfile_label = ws.workfile_name or os.path.basename(ws.workfile_path)
        dirty_marker = " ●" if ws.dirty else ""
        st.markdown(f"**{workfile_label}**{dirty_marker}")
        if ws.last_saved_by:
            st.caption(f"Saved by {ws.last_saved_by}")
            st.caption(_format_uk_time(ws.last_saved_at))
        st.divider()

    # New / Open — active only when no workfile is open
    if st.button("New workfile", use_container_width=True, disabled=has_workfile):
        st.session_state["show_new_form"] = True
        st.session_state.pop("show_open_form", None)
        st.rerun()

    if st.button("Open workfile", use_container_width=True, disabled=has_workfile):
        st.session_state["show_open_form"] = True
        st.session_state.pop("show_new_form", None)
        st.rerun()

    st.divider()

    # Save / Save and Close / Close Without Saving — active only when a workfile is open
    if st.button("Save", use_container_width=True, disabled=not has_workfile):
        save_workfile(ws, st.session_state["username"])
        st.rerun()

    if st.button("Save as", use_container_width=True, disabled=not has_workfile):
        st.session_state["show_save_as_form"] = True
        st.rerun()

    if st.button("Save and close", use_container_width=True, disabled=not has_workfile):
        save_workfile(ws, st.session_state["username"])
        close_workfile(ws)
        st.session_state.pop("workfile_state", None)
        _clear_workfile_session_state()
        st.rerun()

    if st.button("Close without saving", use_container_width=True, disabled=not has_workfile):
        if has_workfile and ws.dirty:
            st.session_state["confirm_close_without_saving"] = True
        else:
            close_workfile(ws)
            st.session_state.pop("workfile_state", None)
            _clear_workfile_session_state()
        st.rerun()

    st.divider()
    st.caption(f"Signed in as {st.session_state.get('username', '')}")
    if st.button("Sign out", use_container_width=True):
        if ws:
            close_workfile(ws)
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()



# ---------------------------------------------------------------------------
# Sidebar action dialogs
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# New workfile form
# ---------------------------------------------------------------------------

def _pick_folder() -> str:
    """Open a native Windows folder picker via tkinter. Returns path or empty string."""
    try:
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk()
        root.withdraw()
        root.wm_attributes("-topmost", True)
        folder = filedialog.askdirectory(title="Select save location for new workfile")
        root.destroy()
        return folder or ""
    except Exception:
        return ""


def _show_new_workfile_form():
    from modules.m01_data_acquisition.api_client import get_projects, get_submissions, get_organisations
    from modules.constants_temp.constants_temp import ORGANISATIONS_FIELDNAMES as ORG_FIELDS

    st.caption("All fields required.")

    CURRENT_YEAR = datetime.date.today().year
    YEAR_OPTIONS = [CURRENT_YEAR, CURRENT_YEAR - 1]
    selected_year = st.selectbox("Year", options=YEAR_OPTIONS, index=0, key="np_year")

    @st.cache_data(show_spinner=False)
    def _fetch_projects(year, token):
        return get_projects(year, token)

    with st.spinner(f"Loading projects for {selected_year}…"):
        try:
            project_list = _fetch_projects(selected_year, st.session_state["token"])
            project_options = {p["project_name"]: p["project_id"] for p in project_list}
        except Exception as e:
            st.error(f"Could not load project list: {e}")
            project_options = {}

    selected_project_name = st.selectbox(
        "Project", options=list(project_options.keys()), index=None,
        placeholder="Select a project…", key="np_project", disabled=not project_options,
    )
    selected_project_id = project_options.get(selected_project_name, "")

    workfile_name = st.text_input(
        "Workfile name",
        value=selected_project_name or "",
        key="np_workfile_name",
        help="Used as the file name (without .cgw).",
    )

    col_browse, col_clear = st.columns([2, 1])
    with col_browse:
        if st.button("📂  Browse for save location…", key="np_browse", use_container_width=True):
            picked = _pick_folder()
            if picked:
                st.session_state["np_save_folder_val"] = picked
            st.rerun()
    with col_clear:
        if st.button("Clear", key="np_clear", disabled=not st.session_state.get("np_save_folder_val")):
            st.session_state["np_save_folder_val"] = ""
            st.rerun()

    folder_val = st.session_state.get("np_save_folder_val", "")
    if folder_val:
        st.success(f"✔  {folder_val}")
    else:
        st.caption("No location selected.")

    st.divider()

    if st.button("Create workfile", type="primary", key="np_create"):
        errors = []
        if not selected_project_id:
            errors.append("Please select a project.")
        if not workfile_name.strip():
            errors.append("Please enter a workfile name.")
        folder = st.session_state.get("np_save_folder_val", "").strip()
        if not folder:
            errors.append("Please enter a save location.")
        elif not os.path.isdir(folder):
            errors.append(f"Save location not found: {folder}")
        if errors:
            for e in errors:
                st.error(e)
            return

        workfile_path = os.path.join(folder, f"{workfile_name.strip()}.cgw")

        with st.spinner("Fetching project data…"):
            try:
                token = st.session_state["token"]
                org_rows = get_organisations(int(selected_year), token)
                submission_rows = get_submissions(int(selected_project_id), int(selected_year), token)
                if not submission_rows:
                    st.error("No submissions found for this project and year.")
                    return
            except Exception as e:
                st.error(f"Could not load submissions: {e}")
                return

        ws_new = new_workfile(workfile_path, workfile_name.strip())
        ws_new.settings = {
            "year":                    str(selected_year),
            "project_id":              str(selected_project_id),
            "project_name":            selected_project_name,
            "cleaned_template_path":   "",
            "ppt_template_path":       "",
            "selected_submission_id":  "",
            "batch_cursor":            "0",
        }

        ws_new.organisations = [
            {f: row.get(f, "") for f in ORG_FIELDS} for row in org_rows
        ]

        org_lookup = {str(r["organisation_id"]): r for r in org_rows}
        rows_out = []
        for row in submission_rows:
            services = row.get("services", [])
            org = org_lookup.get(str(row["organisation_id"]), {})
            rows_out.append({
                "submission_id":            row["submission_id"],
                "submission_code":          row["submission_code"],
                "submission_name":          row["submission_name"],
                "submission_year":          row.get("submission_year", ""),
                "project_id":               row.get("project_id", ""),
                "project_name":             row.get("project_name", ""),
                "organisation_id":          row["organisation_id"],
                "organisation_name":        row["organisation_name"],
                "submission_service_count": row.get("submission_service_count", ""),
                "response_count":           row.get("response_count", ""),
                "submission_level":         row.get("submission_level", ""),
                "service_item_ids":   "|".join(str(s["service_item_id"])   for s in services),
                "service_item_names": "|".join(str(s["service_item_name"]) for s in services),
                "service_response_counts": "|".join(str(s["response_count"]) for s in services),
                "Region()":                org.get("region_name", ""),
            })
        ws_new.submissions = rows_out

        ws_new.locked_by = st.session_state["username"]
        write_lock(workfile_path, st.session_state["username"])
        save_workfile(ws_new, st.session_state["username"])

        st.session_state["workfile_state"] = ws_new
        st.session_state.pop("show_new_form", None)
        st.session_state.pop("np_save_folder", None)
        _clear_workfile_session_state()
        st.rerun()


# ---------------------------------------------------------------------------
# Save As form
# ---------------------------------------------------------------------------

def _show_save_as_form():
    import shutil

    ws_cur = _ws()
    s = ws_cur.settings

    st.caption("Choose a new location and/or name. The cleaned PowerPoint template is copied alongside it.")

    workfile_name = st.text_input(
        "Workfile name",
        value=ws_cur.workfile_name or "",
        key="sa_workfile_name",
        help="Used as the file name (without .cgw).",
    )

    col_browse, col_clear = st.columns([2, 1])
    with col_browse:
        if st.button("📂  Browse for save location…", key="sa_browse", use_container_width=True):
            picked = _pick_folder()
            if picked:
                st.session_state["sa_save_folder_val"] = picked
            st.rerun()
    with col_clear:
        if st.button("Clear", key="sa_clear", disabled=not st.session_state.get("sa_save_folder_val")):
            st.session_state["sa_save_folder_val"] = ""
            st.rerun()

    folder_val = st.session_state.get("sa_save_folder_val", "")
    if folder_val:
        st.success(f"✔  {folder_val}")
    else:
        st.caption("No location selected.")

    st.divider()
    col_save, col_cancel = st.columns([1, 1])

    def _do_save_as(new_workfile_path: str, new_name: str):
        old_workfile_path = ws_cur.workfile_path
        old_template_path = (s.get("cleaned_template_path") or "").strip()

        # Copy the cleaned template alongside the new .cgw, renamed to match
        if old_template_path and os.path.exists(old_template_path):
            new_template_path = os.path.join(os.path.dirname(new_workfile_path), f"{new_name}.pptx")
            shutil.copyfile(old_template_path, new_template_path)
            s["cleaned_template_path"] = new_template_path
            s["ppt_template_path"] = new_template_path

        ws_cur.workfile_name = new_name
        write_lock(new_workfile_path, st.session_state["username"])
        ws_cur.locked_by = st.session_state["username"]
        save_workfile(ws_cur, st.session_state["username"], target_path=new_workfile_path)

        # Release the lock on the old file — we've moved away from it
        if old_workfile_path and old_workfile_path != new_workfile_path and os.path.exists(old_workfile_path):
            try:
                clear_lock(old_workfile_path)
            except Exception:
                pass

        st.session_state.pop("show_save_as_form", None)
        st.session_state.pop("sa_save_folder_val", None)
        st.session_state.pop("sa_confirm_overwrite_path", None)
        st.rerun()

    if col_save.button("Save as", type="primary", key="sa_save"):
        errors = []
        name = workfile_name.strip()
        if not name:
            errors.append("Please enter a workfile name.")
        folder = folder_val.strip()
        if not folder:
            errors.append("Please choose a save location.")
        elif not os.path.isdir(folder):
            errors.append(f"Save location not found: {folder}")
        if errors:
            for e in errors:
                st.error(e)
        else:
            new_workfile_path = os.path.join(folder, f"{name}.cgw")
            if os.path.exists(new_workfile_path):
                st.session_state["sa_confirm_overwrite_path"] = new_workfile_path
                st.session_state["sa_confirm_overwrite_name"] = name
                st.rerun()
            else:
                _do_save_as(new_workfile_path, name)

    if col_cancel.button("Cancel", key="sa_cancel"):
        st.session_state.pop("show_save_as_form", None)
        st.session_state.pop("sa_save_folder_val", None)
        st.rerun()

    overwrite_path = st.session_state.get("sa_confirm_overwrite_path")
    if overwrite_path:
        st.warning(f"A file already exists at {overwrite_path}. Overwrite it?")
        c1, c2 = st.columns(2)
        if c1.button("Overwrite", type="primary", key="sa_overwrite_confirm"):
            _do_save_as(overwrite_path, st.session_state.get("sa_confirm_overwrite_name", workfile_name.strip()))
        if c2.button("Cancel", key="sa_overwrite_cancel"):
            st.session_state.pop("sa_confirm_overwrite_path", None)
            st.session_state.pop("sa_confirm_overwrite_name", None)
            st.rerun()


# ---------------------------------------------------------------------------
# Open workfile form
# ---------------------------------------------------------------------------

def _pick_workfile_file() -> str:
    """Open a native Windows file picker for .cgw files."""
    try:
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk()
        root.withdraw()
        root.wm_attributes("-topmost", True)
        path = filedialog.askopenfilename(
            title="Open ChartGen workfile",
            filetypes=[("ChartGen workfile", "*.cgw"), ("All files", "*.*")],
        )
        root.destroy()
        return path or ""
    except Exception:
        return ""


def _show_open_workfile_form():
    col_browse2, col_clear2 = st.columns([2, 1])
    with col_browse2:
        if st.button("📂  Browse for .cgw file…", key="op_browse", use_container_width=True):
            picked = _pick_workfile_file()
            if picked:
                st.session_state["op_workfile_path_val"] = picked
            st.rerun()
    with col_clear2:
        if st.button("Clear", key="op_clear", disabled=not st.session_state.get("op_workfile_path_val")):
            st.session_state["op_workfile_path_val"] = ""
            st.rerun()

    workfile_path_val = st.session_state.get("op_workfile_path_val", "")
    if workfile_path_val:
        st.success(f"✔  {workfile_path_val}")
    else:
        st.caption("No file selected.")

    st.divider()

    if st.button("Open", type="primary", key="op_open"):
        path = st.session_state.get("op_workfile_path_val", "").strip()
        if not path:
            st.error("Please enter a path.")
            return
        if not os.path.exists(path):
            st.error("File not found.")
            return
        if not path.endswith(".cgw"):
            st.error("Please select a .cgw file.")
            return

        info = read_workfile_info(path)
        if info.get("locked_by"):
            st.session_state["op_lock_warning_path"] = path
            st.session_state["op_lock_warning_info"] = info
            st.rerun()
        else:
            write_lock(path, st.session_state["username"])
            ws = open_workfile(path)
            ws.locked_by = st.session_state["username"]
            st.session_state["workfile_state"] = ws
            st.session_state.pop("show_open_form", None)
            st.session_state.pop("op_workfile_path", None)
            _clear_workfile_session_state()
            st.rerun()

    # Lock warning — shown inline, does not force re-login
    lock_path = st.session_state.get("op_lock_warning_path")
    if lock_path:
        lock_info = st.session_state.get("op_lock_warning_info", {})
        st.warning(
            f"This workfile was opened by **{lock_info.get('locked_by', 'unknown')}** "
            f"on {lock_info.get('locked_at', 'an unknown time')}. "
            "Are you sure you want to open it?"
        )
        c1, c2 = st.columns(2)
        if c1.button("Open anyway", type="primary", key="op_lock_confirm"):
            write_lock(lock_path, st.session_state["username"])
            ws = open_workfile(lock_path)
            ws.locked_by = st.session_state["username"]
            st.session_state["workfile_state"] = ws
            st.session_state.pop("show_open_form", None)
            st.session_state.pop("op_workfile_path", None)
            st.session_state.pop("op_lock_warning_path", None)
            st.session_state.pop("op_lock_warning_info", None)
            _clear_workfile_session_state()
            st.rerun()
        if c2.button("Cancel", key="op_lock_cancel"):
            st.session_state.pop("op_lock_warning_path", None)
            st.session_state.pop("op_lock_warning_info", None)
            st.rerun()


if st.session_state.get("confirm_close_without_saving"):
    st.warning("Close without saving? Unsaved changes will be lost.")
    c1, c2 = st.columns(2)
    if c1.button("Close without saving", type="primary"):
        close_workfile(ws)
        st.session_state.pop("workfile_state", None)
        _clear_workfile_session_state()
        st.session_state.pop("confirm_close_without_saving", None)
        st.rerun()
    if c2.button("Cancel"):
        st.session_state.pop("confirm_close_without_saving", None)
        st.rerun()
    st.stop()

if st.session_state.get("show_new_form"):
    st.title("New Workfile")
    _show_new_workfile_form()
    st.stop()

if st.session_state.get("show_open_form"):
    st.title("Open Workfile")
    _show_open_workfile_form()
    st.stop()

if st.session_state.get("show_save_as_form"):
    st.title("Save Workfile As")
    _show_save_as_form()
    st.stop()


# ---------------------------------------------------------------------------
# No-workfile-loaded state
# ---------------------------------------------------------------------------

if not _has_workfile():
    st.title("ChartGen")
    st.caption("Analysis and Reporting software")
    st.info("No workfile open. Use the sidebar to create a new workfile or open an existing one.")
    st.stop()


# ---------------------------------------------------------------------------
# Main app — tabs
# ---------------------------------------------------------------------------

st.title("ChartGen")
st.caption("Analysis and Reporting software")

(tab_details, tab_config, tab_imports, tab_select,
 tab_text, tab_running_order, tab_charts, tab_batches) = st.tabs([
    "Details", "Config", "Imports", "Select",
    "Text", "Running Order", "Charts", "Batches"
])


# ---------------------------------------------------------------------------
# Details tab
# ---------------------------------------------------------------------------

with tab_details:
    st.header("Project Details")
    st.caption("These settings were configured at workfile creation.")
    s = _settings()
    st.markdown(f"**Year** &nbsp;&nbsp; {s.get('year', '—')}")
    st.markdown(f"**Project** &nbsp;&nbsp; {s.get('project_name', '—')}")
    st.markdown(f"**Project ID** &nbsp;&nbsp; `{s.get('project_id', '—')}`")
    st.markdown(f"**File** &nbsp;&nbsp; `{_ws().workfile_path}`")
    if _ws().last_saved_by:
        st.markdown(f"**Last saved by** &nbsp;&nbsp; {_ws().last_saved_by}")
        st.markdown(f"**Last saved at** &nbsp;&nbsp; {_format_uk_time(_ws().last_saved_at)}")


# ---------------------------------------------------------------------------
# Config tab
# ---------------------------------------------------------------------------

with tab_config:
    st.header("User Controlled Configuration Files")
    st.info("Config file management coming soon.")


# ---------------------------------------------------------------------------
# Select tab
# ---------------------------------------------------------------------------

with tab_select:
    import pandas as pd

    st.header("Selection & Populations")
    submissions = _submissions()

    st.subheader("Select reporting unit")

    if not submissions:
        st.warning("No submissions loaded.")
    else:
        display_mode = st.radio(
            "Identify by",
            options=["Submission name", "Submission code", "Submission ID"],
            horizontal=True, key="select_display_mode",
        )

        def _submission_label(row):
            if display_mode == "Submission code":
                return f"{row['submission_code']}  —  {row['submission_name']}"
            elif display_mode == "Submission ID":
                return f"{row['submission_id']}  —  {row['submission_name']}"
            else:
                return row["submission_name"]

        label_to_id = {_submission_label(r): r["submission_id"] for r in submissions}
        saved_unit = _settings().get("selected_submission_id", "")
        saved_label = next((lbl for lbl, sid in label_to_id.items() if sid == saved_unit), None)
        unit_index = list(label_to_id.keys()).index(saved_label) if saved_label in label_to_id else None

        selected_label = st.selectbox(
            "Reporting unit", options=list(label_to_id.keys()), index=unit_index,
            placeholder="Select a reporting unit…", key="select_unit",
        )
        selected_id = label_to_id.get(selected_label, "")

        if selected_id:
            if selected_id != saved_unit:
                s = _settings()
                s["selected_submission_id"] = str(selected_id)
                _save_settings(s)

            selected_row = next((r for r in submissions if r["submission_id"] == selected_id), None)
            if selected_row:
                c1, c2, c3 = st.columns(3)
                c1.metric("Submission ID",  selected_row["submission_id"])
                c2.metric("Code",           selected_row["submission_code"])
                c3.metric("Organisation",   selected_row["organisation_name"])

    st.divider()
    st.subheader("Populations")
    st.caption("Item tables define the comparator population.")

    def _submissions_to_display_rows(rows: list, expand_services: bool = False) -> list:
        """Prepare submission rows for display in the Populations table, optionally expanding services into one row each."""
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

    with st.expander("Submissions — item table", expanded=st.session_state.get("pop_expander_open", True)):
        if not submissions:
            st.info("No submissions data.")
        else:
            col_toggle1, col_toggle2 = st.columns([2, 2])
            expand_services = col_toggle1.toggle(
                "Show services as separate rows",
                value=st.session_state.get("pop_expand_services_val", False), key="pop_expand_services",
            )
            include_org = col_toggle2.toggle(
                "Include organisational-level submissions",
                value=st.session_state.get("pop_include_org_val", False), key="pop_include_org",
            )
            st.session_state["pop_expand_services_val"] = expand_services
            st.session_state["pop_include_org_val"] = include_org
            st.session_state["pop_expander_open"] = True

            display_rows = submissions if include_org else [
                r for r in submissions if r.get("submission_level", "") != "O"
            ]
            display_rows = _submissions_to_display_rows(display_rows, expand_services)

            display_cols = [
                "submission_id", "submission_code", "submission_name",
                "organisation_name", "response_count", "submission_service_count",
                "service_item_ids", "service_item_names", "service_response_counts", "Region()",
            ]
            df = pd.DataFrame(display_rows)[display_cols] if display_rows else pd.DataFrame(columns=display_cols)
            df.columns = [
                "ID", "Code", "Name", "Organisation", "Responses", "Service count",
                "Service IDs", "Service names", "Service responses", "Region()",
            ]
            st.dataframe(df, use_container_width=True, hide_index=True)
            st.caption(f"{len(display_rows)} row(s)")


# ---------------------------------------------------------------------------
# Imports tab
# ---------------------------------------------------------------------------

with tab_imports:
    st.header("Import Project Data")
    st.subheader("PowerPoint Template")

    s = _settings()
    current_ppt_path    = s.get("ppt_template_path", "")
    current_cleaned_path = s.get("cleaned_template_path", "")

    if current_ppt_path:
        st.caption(f"Template: `{current_ppt_path}`")
    if current_cleaned_path:
        st.caption(f"Cleaned template: `{current_cleaned_path}`")

    uploaded_template = st.file_uploader(
        "Upload PowerPoint template (.pptx)", type=["pptx"],
        key="ppt_template_uploader",
        help="Named chart placeholders are read automatically. "
             "Yellow textboxes containing toolkit URLs are extracted and stripped.",
    )

    if uploaded_template is not None:
        if st.button("Process Template"):
            from modules.m02_template_reader.template_reader import read_template, update_urls_csv
            from modules.m03_running_order.running_order import generate_from_template

            ws_cur = _ws()
            workfile_dir = os.path.dirname(ws_cur.workfile_path)
            workfile_name = ws_cur.workfile_name or "template"
            cleaned_path = os.path.join(workfile_dir, f"{workfile_name}.pptx")

            # Step 1 — Read template
            raw_bytes = uploaded_template.getbuffer()
            import tempfile
            with tempfile.NamedTemporaryFile(suffix=".pptx", delete=False) as tmp:
                tmp.write(raw_bytes)
                tmp_path = tmp.name

            with st.spinner("Step 1 of 3 — Reading template…"):
                try:
                    result = read_template(tmp_path)
                except Exception as e:
                    st.error(f"Template read failed: {e}")
                    os.unlink(tmp_path)
                    st.stop()
            os.unlink(tmp_path)

            # Save cleaned template to disk alongside .cgw
            with open(cleaned_path, "wb") as f:
                f.write(result.cleaned_pptx_bytes)

            # Store reference copy in WorkfileState
            ws_cur.template_pptx_bytes = result.cleaned_pptx_bytes

            s = _settings()
            s["cleaned_template_path"] = cleaned_path
            s["ppt_template_path"] = cleaned_path
            _save_settings(s)

            with_url = [p for p in result.placeholders if p.url]
            without_url = [p for p in result.placeholders if not p.url]
            st.success(
                f"Template read — {len(result.placeholders)} placeholder(s): "
                f"{len(with_url)} with URL, {len(without_url)} empty."
            )
            if result.warnings:
                for w in result.warnings:
                    st.warning(w)

            # Step 2 — Fetch chart data
            new_urls = [{"url": p.url, "label": p.label} for p in result.placeholders if p.url]
            if new_urls:
                # Merge into WorkfileState urls
                existing = {u["url"] for u in ws_cur.urls}
                added = 0
                for u in new_urls:
                    if u["url"] not in existing:
                        ws_cur.urls.append(u)
                        added += 1
                already = len(new_urls) - added
                st.info(f"urls — {added} new URL(s) added, {already} already present. Fetching…")

                progress_bar = st.progress(0)
                status_text = st.empty()

                def _on_fetch_progress(current, total, label):
                    progress_bar.progress(current / total)
                    status_text.text(f"Step 2 of 3 — Fetching {current}/{total}: {label}")

                with st.spinner("Step 2 of 3 — Fetching chart data…"):
                    fetch_results = fetch_all(
                        st.session_state["token"],
                        on_progress=_on_fetch_progress,
                        workfile_state=ws_cur,
                    )
                status_text.empty()
                progress_bar.empty()

                ok  = [r for r in fetch_results if r["status"] == "ok"]
                err = [r for r in fetch_results if r["status"] != "ok"]
                st.success(f"Data fetch complete — {len(ok)} succeeded, {len(err)} failed.")
                for r in err:
                    st.error(f"✗ [{r['tier_id']}] {r['label']} — {r['message']}")
            else:
                st.info("No URLs found in template. Skipping data fetch.")

            # Step 3 — Generate Running Order
            with st.spinner("Step 3 of 3 — Generating Running Order…"):
                manifest = _manifest()
                rows = generate_from_template(result, manifest)
                ws_cur.running_order_rows = rows
                ws_cur.dirty = True
                st.success(f"Running Order generated — {len(rows)} rows.")

            st.session_state["template_result"] = result

    st.divider()
    st.subheader("Toolkit API — Fetch Chart Data")
    if st.button("Fetch All Chart Data"):
        progress_bar = st.progress(0)
        status_text = st.empty()

        def on_progress(current, total, label):
            progress_bar.progress(current / total)
            status_text.text(f"Fetching {current}/{total}: {label}")

        with st.spinner("Fetching data…"):
            fetch_results = fetch_all(
                st.session_state["token"],
                on_progress=on_progress,
                workfile_state=_ws(),
            )
        status_text.empty()
        progress_bar.empty()

        for r in fetch_results:
            if r["status"] == "ok":
                st.success(f"✓ [{r['tier_id']}] {r['label']} — {r['message']}")
            else:
                st.error(f"✗ [{r['tier_id']}] {r['label']} — {r['message']}")


# ---------------------------------------------------------------------------
# Text tab
# ---------------------------------------------------------------------------

with tab_text:
    st.header("Text — Flag Tokens")
    st.caption(
        "Add `update_text` rows to the Running Order to replace these tokens "
        "in your PowerPoint template at generation time."
    )
    from modules.m12_local_config.local_config import build_report_context as _brc_text
    _rc_text = _brc_text(_settings(), _submissions())
    _preview_value = _rc_text.submission_name if _rc_text else "— no reporting unit selected —"

    st.dataframe(
        {
            "Token": ["[selected-reporting-unit-name]"],
            "Replaced with": ["Submission name"],
            "Current value": [_preview_value],
        },
        use_container_width=True, hide_index=True,
    )


# ---------------------------------------------------------------------------
# Running Order tab
# ---------------------------------------------------------------------------

with tab_running_order:
    st.header("Running Order")

    ws_ro = _ws()
    if not ws_ro.running_order_rows:
        st.info("No Running Order found. Upload and process a PowerPoint template in the Imports tab.")
    else:
        try:
            import io
            import pandas as pd
            from modules.m03_running_order.running_order import (
                read_xlsx, write_xlsx, COLUMNS, ALL_FUNCTIONS
            )

            manifest = _manifest()
            cache_to_shape = {fname: entry.get("shape_type", "") for fname, entry in manifest.items()}
            cache_to_label = {fname: entry.get("label", fname) for fname, entry in manifest.items()}

            chart_type_by_shape = {}
            if os.path.exists(CHART_TYPE_MAP_PATH):
                import csv as _csv
                with open(CHART_TYPE_MAP_PATH, newline="", encoding="utf-8-sig") as _ctf:
                    for _ctr in _csv.DictReader(_ctf):
                        _shape = _ctr.get("data_shape", "").strip()
                        _ref   = _ctr.get("chart_type_ref", "").strip()
                        if _shape and _ref:
                            chart_type_by_shape.setdefault(_shape, []).append(_ref)

            rows = ws_ro.running_order_rows

            @st.dialog("Edit row", width="large")
            def _row_edit_dialog(sel_idx):
                row  = ws_ro.running_order_rows[sel_idx]
                func = str(row.get("function", ""))
                is_insert_chart    = func == "insert_chart"
                is_set_default_pop = func == "set_default_populations"
                is_content         = func in {"insert_chart", "empty_placeholder"}
                needs_populations  = is_insert_chart or is_set_default_pop

                st.caption(f"Row {row['row_id']}  ·  {func}")
                if is_content:
                    st.caption(f"Placeholder: **{row.get('placeholder', '')}**  ·  Slide: **{row.get('slide_index', '')}**")

                f_enabled = st.checkbox("Enabled", value=(row.get("enabled", 1) == 1))
                f_notes   = st.text_input("Notes", value=str(row.get("notes", "") or ""))

                if is_insert_chart:
                    cache_file = str(row.get("cache_file", "") or "")
                    shape_type = cache_to_shape.get(cache_file, "")
                    valid_refs = chart_type_by_shape.get(shape_type, []) or [
                        ref for refs in chart_type_by_shape.values() for ref in refs
                    ]
                    label_hint = cache_to_label.get(cache_file, cache_file)
                    shape_hint = f"  ·  {shape_type}" if shape_type else ""
                    st.caption(f"Data: {label_hint}{shape_hint}")

                    current_ref = str(row.get("chart_type_ref", "") or "")
                    ref_options = [""] + valid_refs
                    try:
                        ref_index = ref_options.index(current_ref)
                    except ValueError:
                        ref_index = 0

                    f_chart_type = st.selectbox(
                        "Chart type", options=ref_options, index=ref_index,
                        format_func=lambda v: "— select chart type —" if v == "" else v,
                    )
                    with st.expander("Position & size"):
                        pc1, pc2, pc3, pc4 = st.columns(4)
                        pc1.metric("Left EMU",   row.get("left_emu",   ""))
                        pc2.metric("Top EMU",    row.get("top_emu",    ""))
                        pc3.metric("Width EMU",  row.get("width_emu",  ""))
                        pc4.metric("Height EMU", row.get("height_emu", ""))
                else:
                    f_chart_type = row.get("chart_type_ref", "")

                if needs_populations:
                    from modules.m12_local_config.local_config import get_peer_group_columns
                    _peer_cols = get_peer_group_columns(_submissions())
                    _pop_options = ["All"] + _peer_cols + ["Selected"]
                    current_pop_str = str(row.get("populations", "") or "")
                    if is_insert_chart and not current_pop_str:
                        current_pop_list = []
                        _pop_help = "Leave blank to inherit the default populations set above."
                    else:
                        current_pop_list = [p.strip() for p in current_pop_str.split("^") if p.strip() and p.strip() in _pop_options]
                        _pop_help = "Order is fixed: All → peer groups → Selected."

                    f_populations_selected = st.multiselect(
                        "Populations" + (" (override — blank = use default)" if is_insert_chart else ""),
                        options=_pop_options, default=current_pop_list, help=_pop_help,
                    )
                    f_populations = "^".join(p for p in _pop_options if p in f_populations_selected)
                else:
                    f_populations = str(row.get("populations", "") or "")

                st.divider()
                col_apply, col_cancel = st.columns([1, 1])

                if col_apply.button("Apply", type="primary"):
                    ws_ro.running_order_rows[sel_idx]["enabled"] = 1 if f_enabled else 0
                    ws_ro.running_order_rows[sel_idx]["notes"]   = f_notes
                    if is_insert_chart:
                        ws_ro.running_order_rows[sel_idx]["chart_type_ref"] = f_chart_type
                    if needs_populations:
                        ws_ro.running_order_rows[sel_idx]["populations"] = f_populations
                    ws_ro.dirty = True
                    st.session_state["ro_selected_idx"] = None
                    st.rerun()

                if col_cancel.button("Cancel"):
                    st.session_state["ro_selected_idx"] = None
                    st.rerun()

            if not rows:
                st.info("Running Order is empty.")
            else:
                def _short_func(f):
                    return {
                        "create_ppt":              "▶  create_ppt",
                        "set_default_populations": "◉  set_default_populations",
                        "save_ppt":                "■  save_ppt",
                        "save_pdf":                "■  save_pdf",
                        "insert_chart":            "◈  insert_chart",
                        "empty_placeholder":       "○  empty_placeholder",
                        "update_text":             "✎  update_text",
                    }.get(f, f)

                overview_df = pd.DataFrame({
                    "#":           [r["row_id"] for r in rows],
                    "On":          ["✓" if r["enabled"] == 1 else "–" for r in rows],
                    "Function":    [_short_func(str(r.get("function", ""))) for r in rows],
                    "Slide":       [r.get("slide_index", "") for r in rows],
                    "Placeholder": [r.get("placeholder", "") for r in rows],
                    "Chart type":  [r.get("chart_type_ref", "") for r in rows],
                    "Notes":       [r.get("notes", "") for r in rows],
                })

                selection = st.dataframe(
                    overview_df, use_container_width=True, hide_index=True,
                    height=min(36 * len(rows) + 38, 540),
                    on_select="rerun", selection_mode="single-row",
                )
                selected_rows = selection.selection.get("rows", [])
                st.session_state["ro_selected_idx"] = selected_rows[0] if selected_rows else None
                sel_idx = st.session_state["ro_selected_idx"]

                col_edit, col_dl, col_ul = st.columns([1, 1, 1])

                edit_label = (
                    f"✎  Edit row {rows[sel_idx]['row_id']}" if sel_idx is not None else "✎  Edit row"
                )
                edit_clicked = col_edit.button(
                    edit_label, disabled=(sel_idx is None), type="secondary", use_container_width=True,
                )

                _ro_buffer = io.BytesIO()
                write_xlsx(
                    rows, _ro_buffer,
                    chart_type_map_path=CHART_TYPE_MAP_PATH, manifest=manifest,
                )
                col_dl.download_button(
                    label="⬇  Download Running Order", data=_ro_buffer.getvalue(),
                    file_name="running_order.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                )

                if col_ul.button("⬆  Upload Running Order", use_container_width=True):
                    st.session_state["ro_show_uploader"] = not st.session_state.get("ro_show_uploader", False)

                if st.session_state.get("ro_show_uploader", False):
                    uploaded_ro = st.file_uploader(
                        "Upload Running Order", type=["xlsx"], key="ro_uploader",
                        label_visibility="collapsed",
                    )
                    if uploaded_ro is not None:
                        ws_ro.running_order_rows = read_xlsx(io.BytesIO(uploaded_ro.getbuffer()))
                        ws_ro.dirty = True
                        st.session_state["ro_show_uploader"] = False
                        st.rerun()

                if edit_clicked and sel_idx is not None:
                    _row_edit_dialog(sel_idx)

        except ImportError:
            st.warning("Install openpyxl and pandas to use the Running Order editor.")
        except Exception as _e:
            st.error(f"Could not load Running Order: {_e}")


# ---------------------------------------------------------------------------
# Charts tab
# ---------------------------------------------------------------------------

with tab_charts:
    st.header("Chart Preview")

    cached_files = _cached_files()
    manifest = _manifest()

    if not cached_files:
        st.info("No cached chart data found. Use the Imports tab to fetch data first.")
    else:
        def file_label(f):
            entry = manifest.get(f, {})
            label = entry.get("label", "")
            return f"{f}  —  {label}" if label else f

        file_options = {file_label(f): f for f in cached_files}
        selected_label = st.selectbox("Select a cached dataset", options=list(file_options.keys()), index=0)
        selected_file = file_options[selected_label]

        shape, shape_type = _load_shape_ps(selected_file)
        valid_types = get_valid_chart_types(shape_type)
        st.caption(f"Shape type: **{shape_type}**")

        if not valid_types:
            st.warning(f"No Base Charts defined for shape type '{shape_type}'.")
        else:
            type_options = {desc: ref for ref, desc in valid_types}
            selected_desc = st.selectbox(
                "Select a Base Chart", options=list(type_options.keys()),
                index=None, placeholder="Choose a chart type to render…",
            )

            if selected_desc:
                chart_ref = type_options[selected_desc]
                from modules.m12_local_config.local_config import build_report_context
                from modules.m06_assembly_engine.assembly_engine import build_population_shapes
                from modules.m04_data_shapes.shapes import PopulationShape

                _subs = _submissions()
                _rc = build_report_context(_settings(), _subs)
                if _rc:
                    st.caption(f"Highlighting: **{_rc.submission_code}** — {_rc.submission_name}")

                _default_pop = _settings().get("default_populations", "All^Selected") or "All^Selected"
                try:
                    _pop_shapes = build_population_shapes(shape, _default_pop, _subs, _rc)
                except Exception:
                    _pop_shapes = []
                if not _pop_shapes:
                    _pop_shapes = [PopulationShape(role="All", label="All", shape=shape)]

                with st.spinner("Rendering…"):
                    image_bytes, autotable_stats = render_chart(
                        chart_ref, _pop_shapes, width=80, height=50, report_context=_rc
                    )
                st.image(image_bytes, use_container_width=True)

                if autotable_stats:
                    st.caption("Autotable statistics")
                    st.json(autotable_stats)


# ---------------------------------------------------------------------------
# Batches tab
# ---------------------------------------------------------------------------

with tab_batches:
    import time as _time
    from modules.m06_assembly_engine.assembly_engine import run_running_order

    _s           = _settings()
    _subs        = _submissions()
    _workfile_dir = os.path.dirname(_ws().workfile_path)
    _cleaned_tpl = _s.get("cleaned_template_path", "").strip()
    _tpl         = _s.get("ppt_template_path", "").strip()
    _active_tpl  = _cleaned_tpl if os.path.exists(_cleaned_tpl) else _tpl
    _sel_id      = str(_s.get("selected_submission_id", "") or "").strip()
    _sel_row     = next((r for r in _subs if str(r["submission_id"]) == _sel_id), None)
    _total       = len(_subs)
    _cursor      = min(int(_s.get("batch_cursor", 0)), _total)
    _outputs_dir = os.path.join(_workfile_dir, "outputs")
    _ro_rows     = _ws().running_order_rows

    st.markdown('<h1 style="font-size:1.8em;margin:0 0 4px 0;padding:0;">Process Outputs</h1>'
                '<hr style="border:none;border-top:1px solid #ddd;margin:0 0 6px 0;">', unsafe_allow_html=True)

    _issues = []
    if not _active_tpl or not os.path.exists(_active_tpl):
        _issues.append("No PowerPoint template configured. Process one in the Imports tab.")
    if not _ro_rows:
        _issues.append("No Running Order found. Process a template in the Imports tab first.")

    _enabled_rows = []
    if not _issues:
        _enabled_rows = [r for r in _ro_rows if r["enabled"] == 1]
        if not _enabled_rows:
            _issues.append("Running Order has rows, but none are enabled. Enable rows in the Running Order tab.")
        _unassigned = [r for r in _enabled_rows if r["function"] == "insert_chart"
                       and not str(r.get("chart_type_ref", "")).strip()]
        if _unassigned:
            _issues.append(f"{len(_unassigned)} insert_chart row(s) have no chart type assigned.")

    if _issues:
        with st.expander("⚠  Setup issues", expanded=True):
            for _iss in _issues:
                st.warning(_iss)

    _can_run = not _issues and bool(_enabled_rows)

    def _build_rows_to_run():
        return [r for r in _ws().running_order_rows if r["enabled"] == 1]

    def _run_for_submissions(submissions_to_run: list, run_label: str):
        from modules.m06_assembly_engine.assembly_engine import (
            run_running_order, AssemblyContext, FUNCTION_MAP
        )
        all_rows    = _build_rows_to_run()
        batch_open  = [r for r in all_rows if str(r.get("scope", "normal")).strip() == "batch_open"]
        normal_rows = [r for r in all_rows if str(r.get("scope", "normal")).strip() == "normal"]
        batch_close = [r for r in all_rows if str(r.get("scope", "normal")).strip() == "batch_close"]

        t_overall = _time.perf_counter()
        if "run_log_rows" not in st.session_state:
            st.session_state["run_log_rows"] = []

        shared_ctx = AssemblyContext()
        base_settings = dict(_s)
        base_settings["cleaned_template_path"] = _active_tpl
        base_settings["outputs_folder"] = _outputs_dir
        base_settings["workfile_state"] = _ws()
        os.makedirs(os.path.join(_outputs_dir, "pptx"), exist_ok=True)
        os.makedirs(os.path.join(_outputs_dir, "pdf"), exist_ok=True)

        for row in batch_open:
            func = FUNCTION_MAP.get(str(row.get("function", "")).strip())
            if func:
                try:
                    func(shared_ctx, row, base_settings)
                except Exception:
                    pass

        for idx, sub in enumerate(submissions_to_run):
            pop_idx = next((i+1 for i, s in enumerate(_subs)
                            if str(s["submission_id"]) == str(sub["submission_id"])), idx+1)

            run_settings = dict(_s)
            run_settings["reporting_unit_name"]    = sub["submission_code"]
            run_settings["selected_submission_id"] = str(sub["submission_id"])
            run_settings["cleaned_template_path"]  = _active_tpl
            run_settings["outputs_folder"]         = _outputs_dir
            run_settings["workfile_state"]         = _ws()

            result = run_running_order(normal_rows, run_settings, ctx=shared_ctx)

            err_msg = ""
            if result["status"] != "ok":
                errs = [e["message"] for e in result["log"] if e["status"] == "error"]
                err_msg = errs[0] if errs else "Unknown error"

            st.session_state["run_log_rows"].append({
                "idx":     pop_idx,
                "code":    sub["submission_code"],
                "name":    sub["submission_name"],
                "ok":      result["status"] == "ok",
                "elapsed": result["elapsed"],
                "error":   err_msg,
            })
            _rows_log = st.session_state["run_log_rows"]
            _bc       = "#e6f4ea" if all(r["ok"] for r in _rows_log) else "#fff3e0"
            _bc_b     = "#4CAF50" if all(r["ok"] for r in _rows_log) else "#E87722"
            _log_placeholder.markdown(
                f"<div style='border-left:4px solid {_bc_b};background:{_bc};"
                f"border-radius:4px;padding:8px 14px;'>"
                f"<table style='width:100%;border-collapse:collapse;'>"
                f"<thead><tr style='font-size:0.78em;color:#666;border-bottom:1px solid #ccc;'>"
                f"<th style='padding:2px 8px;text-align:left;'>#</th>"
                f"<th style='padding:2px 8px;text-align:left;'>Code</th>"
                f"<th style='padding:2px 8px;text-align:left;'>Name</th>"
                f"<th style='padding:2px 8px;text-align:left;'>Status</th>"
                f"<th style='padding:2px 8px;text-align:left;'>Time</th>"
                f"<th style='padding:2px 8px;text-align:left;'>Error</th>"
                f"</tr></thead>"
                f"<tbody>{_build_rows_html(_rows_log)}</tbody>"
                f"</table></div>",
                unsafe_allow_html=True,
            )

        for row in batch_close:
            func = FUNCTION_MAP.get(str(row.get("function", "")).strip())
            if func:
                try:
                    func(shared_ctx, row, base_settings)
                except Exception:
                    pass

        elapsed_total = _time.perf_counter() - t_overall
        ok_count  = sum(1 for r in st.session_state["run_log_rows"] if r["ok"])
        err_count = len(st.session_state["run_log_rows"]) - ok_count
        return ok_count, err_count, elapsed_total

    def _build_rows_html(rows):
        parts = []
        for r in rows:
            status_col  = "#2e7d32" if r["ok"] else "#c62828"
            status_icon = "✓" if r["ok"] else "✗"
            err_td = (
                f'<td style="padding:2px 8px;color:#c62828;font-size:0.9em;">{r["error"]}</td>'
                if r["error"] else "<td></td>"
            )
            parts.append(
                f'<tr style="font-size:0.82em;">'
                f'<td style="padding:2px 8px;color:#888;">{r["idx"]}</td>'
                f'<td style="padding:2px 8px;font-weight:600;">{r["code"]}</td>'
                f'<td style="padding:2px 8px;">{r["name"]}</td>'
                f'<td style="padding:2px 8px;color:{status_col};font-weight:700;">{status_icon}</td>'
                f'<td style="padding:2px 8px;color:#555;">{r["elapsed"]:.1f}s</td>'
                + err_td +
                "</tr>"
            )
        return "".join(parts)

    st.markdown("""<style>
    [data-testid="stSlider"] [data-testid="stThumbValue"] { display:none !important; }
    [data-testid="stSlider"] { padding-bottom:0 !important; margin-bottom:0 !important; }
    </style>""", unsafe_allow_html=True)

    if _can_run:
        _next_sub  = _subs[_cursor] if _cursor < _total else None
        _remaining = _total - _cursor

        st.markdown('<p style="font-weight:600;font-size:0.88em;margin:0 0 2px 0;">Selected reporting unit</p>', unsafe_allow_html=True)
        _r1l, _r1r = st.columns([4, 2])
        with _r1l:
            if _sel_row:
                st.markdown(
                    f'<div style="border-left:4px solid #C12958;padding:4px 10px;background:#fdf0f3;border-radius:4px;line-height:1.35;display:inline-block;width:100%;">'
                    f'<span style="color:#C12958;font-weight:700;font-size:0.74em;letter-spacing:0.05em;">SELECTED REPORTING UNIT</span><br>'
                    f'<span style="font-size:0.92em;font-weight:600;">{_sel_row["submission_name"]}</span><br>'
                    f'<span style="color:#555;font-size:0.8em;">{_sel_row["submission_code"]} &nbsp;·&nbsp; {_sel_row["organisation_name"]}</span>'
                    f'</div>', unsafe_allow_html=True,
                )
            else:
                st.markdown('<p style="color:#888;font-size:0.83em;margin:4px 0;">No reporting unit selected — go to the Select tab.</p>', unsafe_allow_html=True)
        with _r1r:
            _run_selected = st.button(
                f"▶  Run Selected{(' — ' + _sel_row['submission_code']) if _sel_row else ''}",
                disabled=not _sel_row, use_container_width=True, key="btn_run_selected", type="primary",
            )

        st.markdown('<hr style="border:none;border-top:1px solid #ddd;margin:4px 0;">', unsafe_allow_html=True)

        st.markdown('<p style="font-weight:600;font-size:0.88em;margin:0 0 2px 0;">Batch processing</p>', unsafe_allow_html=True)
        _r2l, _r2r = st.columns([4, 2])
        with _r2l:
            if _next_sub:
                st.markdown(f'<p style="font-size:0.81em;color:#444;margin:0;">Next: <strong>{_next_sub["submission_name"]}</strong> ({_next_sub["submission_code"]}) — {_cursor + 1} of {_total}</p>', unsafe_allow_html=True)
            else:
                st.markdown(f'<p style="font-size:0.81em;color:#888;margin:0;">Queue complete — all {_total} reports run.</p>', unsafe_allow_html=True)
            _sl_col, _rs_col = st.columns([3, 2])
            with _sl_col:
                _batch_size = st.slider("Batch size", min_value=1, max_value=min(50, max(_remaining, 1)),
                    value=min(10, max(_remaining, 1)), key="batch_size_slider", label_visibility="collapsed")
            with _rs_col:
                if st.button("↺  Reset queue", key="btn_reset_queue"):
                    _s["batch_cursor"] = "0"
                    _save_settings(_s)
                    st.session_state["run_log_rows"] = []
                    st.rerun()
        with _r2r:
            _run_batch = st.button(
                f"▶▶  Run Batch — next {min(_batch_size, _remaining)}",
                disabled=(_cursor >= _total), use_container_width=True, key="btn_run_batch", type="primary",
            )

        st.markdown('<hr style="border:none;border-top:1px solid #ddd;margin:4px 0;">', unsafe_allow_html=True)

        st.markdown('<p style="font-weight:600;font-size:0.88em;margin:0 0 2px 0;">Full run</p>', unsafe_allow_html=True)
        _r3l, _r3r = st.columns([4, 2])
        with _r3l:
            st.markdown(f'<p style="font-size:0.81em;color:#444;margin:4px 0;">All <strong>{_total}</strong> submissions in the population.</p>', unsafe_allow_html=True)
        with _r3r:
            _run_all = st.button(
                f"▶▶▶  Run All — {_total} reports",
                use_container_width=True, key="btn_run_all", type="primary",
            )

        st.divider()

        if "run_log_rows" not in st.session_state:
            st.session_state["run_log_rows"] = []
        _log_placeholder = st.empty()

        if _run_selected and _sel_row:
            _ok, _err, _elapsed = _run_for_submissions([_sel_row], "Run Selected")

        elif _run_batch and _cursor < _total:
            _batch_subs = _subs[_cursor: _cursor + _batch_size]
            _ok, _err, _elapsed = _run_for_submissions(_batch_subs, f"Run Batch ({len(_batch_subs)})")
            _s["batch_cursor"] = str(_cursor + _ok)
            _save_settings(_s)
            st.rerun()

        elif _run_all:
            _ok, _err, _elapsed = _run_for_submissions(_subs, f"Run All ({_total})")
            _s["batch_cursor"] = str(_ok)
            _save_settings(_s)
            st.rerun()

        if st.session_state.get("run_log_rows"):
            rows_l    = st.session_state["run_log_rows"]
            err_count = sum(1 for r in rows_l if not r["ok"])
            bc        = "#e6f4ea" if err_count == 0 else "#fff3e0"
            bc_border = "#4CAF50" if err_count == 0 else "#E87722"
            _log_placeholder.markdown(
                f"<div style='border-left:4px solid {bc_border};background:{bc};"
                f"border-radius:4px;padding:8px 14px;'>"
                f"<table style='width:100%;border-collapse:collapse;'>"
                f"<thead><tr style='font-size:0.78em;color:#666;border-bottom:1px solid #ccc;'>"
                f"<th style='padding:2px 8px;text-align:left;'>#</th>"
                f"<th style='padding:2px 8px;text-align:left;'>Code</th>"
                f"<th style='padding:2px 8px;text-align:left;'>Name</th>"
                f"<th style='padding:2px 8px;text-align:left;'>Status</th>"
                f"<th style='padding:2px 8px;text-align:left;'>Time</th>"
                f"<th style='padding:2px 8px;text-align:left;'>Error</th>"
                f"</tr></thead>"
                f"<tbody>{_build_rows_html(rows_l)}</tbody>"
                f"</table></div>",
                unsafe_allow_html=True,
            )
