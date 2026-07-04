"""
assembly_engine.py
M06 — Assembly Engine

Executes a Running Order against a PowerPoint template to produce one output file.
All report-building logic lives here. Only this module touches python-pptx directly.

Running Order functions implemented
────────────────────────────────────
  create_ppt          Opens template; saves working copy named for the reporting unit
  insert_chart        Renders a Base Chart and inserts it at the placeholder position
  update_text         Replaces flag tokens in all text shapes with per-unit values
  empty_placeholder   No-op; placeholder has no content assigned
  save_ppt            Saves completed output as .pptx
  save_pdf            Saves completed output as .pdf via COM (requires PowerPoint on machine)

VITAL RULE
──────────
Outputs are ONLY created by functions called from the Running Order.
There are no hidden side-effects. Sub-functions under insert_chart exist solely
to insert the chart — they do not write files, open templates, or touch anything
outside the scope of that single insertion.
"""

import os
import io
import shutil
import time
import traceback

from pptx import Presentation
from pptx.util import Emu
from PIL import Image as PILImage

from modules.m05_chart_engine.cache_reader import load_shape
from modules.m05_chart_engine.base_charts import render_chart
from modules.m12_local_config.local_config import ReportContext, build_report_context
from modules.m04_data_shapes.shapes import PopulationShape, filter_shape
from modules.m07_insert_picture.insert_picture import insert_picture
from modules.m08_insert_from_excel.insert_from_excel import (
    open_excel, close_excel, insert_from_excel
)


def build_population_shapes(data_shape, populations_str: str,
                             submissions: list, report_context) -> list:
    """
    Build an ordered list of PopulationShape objects from a populations string.

    Each token in the string is an intersecting filter applied sequentially to
    the running set of submission_ids. Each resulting set produces a filtered
    copy of the data shape with stats recalculated against that population only.

    'All'      — identity filter; passes all units in the shape
    'Selected' — filters to units belonging to the current organisation_id
    'Name()'   — filters to units whose Name() column value matches the
                 selected unit's value for that column

    The sequential intersection model means:
        Region(Wales)^Hospital_Size(Large)^Selected
    produces three shapes:
        1. Welsh units
        2. Welsh large-hospital units
        3. Welsh large-hospital units belonging to the selected organisation

    This model will become more complex in future. For now, sequential
    intersection is the baseline.

    Returns [] if populations_str is blank or no tokens resolve.
    """
    if not populations_str or not populations_str.strip():
        return []

    # All submission_ids present in the data shape
    shape_ids = {u.submission_id for u in _get_shape_units(data_shape)}
    if not shape_ids:
        return []

    # Build a submission lookup for peer group column resolution
    sub_lookup = {str(r["submission_id"]): r for r in submissions}
    selected_id = str(report_context.submission_id) if report_context else None
    selected_org_id = str(report_context.organisation_id) if report_context else None

    running_ids = set(shape_ids)  # intersection accumulator
    results = []

    for token in populations_str.split("^"):
        token = token.strip()
        if not token:
            continue

        if token == "All":
            token_ids = set(shape_ids)  # identity — no reduction
            label = "All"

        elif token == "Selected":
            if not selected_org_id:
                continue
            token_ids = {
                int(r["submission_id"]) for r in submissions
                if str(r["organisation_id"]) == selected_org_id
                and int(r["submission_id"]) in running_ids
            }
            label = "Selected"

        elif token.endswith("()"):
            col = token
            if not selected_id or selected_id not in sub_lookup:
                continue
            group_value = sub_lookup[selected_id].get(col, "")
            if not group_value:
                continue
            token_ids = {
                int(r["submission_id"]) for r in submissions
                if r.get(col) == group_value
                and int(r["submission_id"]) in running_ids
            }
            label = group_value

        else:
            continue

        # Intersect with running set
        running_ids = running_ids & token_ids
        if not running_ids:
            break

        filtered = filter_shape(data_shape, running_ids)
        results.append(PopulationShape(role=token, label=label, shape=filtered))

    return results


def _get_shape_units(data_shape) -> list:
    """Return the flat list of comparative units from any shape type."""
    from modules.m04_data_shapes.shapes import (
        NumericSeries, NumericCompositional, CategoricalCompositional
    )
    if isinstance(data_shape, NumericSeries):
        return data_shape.units
    elif isinstance(data_shape, (NumericCompositional, CategoricalCompositional)):
        return data_shape.metrics[0].units if data_shape.metrics else []
    return []


# ---------------------------------------------------------------------------
# Assembly context — passed through every function call in a run
# ---------------------------------------------------------------------------

class AssemblyContext:
    def __init__(self):
        self.prs: Presentation = None
        self.output_path: str = ""
        self.template_path: str = ""
        self.log: list[dict] = []
        self.autotable_stats: dict = {}
        self.report_context = None      # set by run_running_order
        self.default_populations: str = ""  # set by set_default_populations row


# ---------------------------------------------------------------------------
# Running Order function implementations
# ---------------------------------------------------------------------------

def create_ppt(ctx: AssemblyContext, row: dict, settings: dict) -> dict:
    """
    Open the cleaned template and set the output path.
    The cleaned template (yellow textboxes already removed) is the source.
    A copy is NOT written to disk at this stage — save_ppt/save_pdf do that.
    """
    template_path = settings.get("cleaned_template_path", "").strip()
    if not template_path or not os.path.exists(template_path):
        # Fall back to the original template if no cleaned version exists
        template_path = settings.get("ppt_template_path", "").strip()

    if not template_path or not os.path.exists(template_path):
        return _err(row, "create_ppt: no template found. Check settings.")

    output_folder = _ensure_output_folder(settings)
    unit_name = (settings.get("reporting_unit_name") or "").strip()
    if not unit_name:
        unit_name = str(settings.get("selected_submission_id") or "output").strip()
    safe_name = _safe_filename(unit_name)
    output_path = os.path.join(output_folder, "pptx", f"{safe_name}.pptx")

    ctx.prs = Presentation(template_path)
    ctx.output_path = output_path
    ctx.template_path = template_path

    return _ok(row, f"Template opened: {os.path.basename(template_path)}")


def set_default_populations(ctx: AssemblyContext, row: dict, settings: dict) -> dict:
    """
    Store the default populations string on AssemblyContext.
    All subsequent insert_chart rows inherit this unless they have their own
    populations value set.
    """
    populations = str(row.get("populations", "") or "").strip()
    ctx.default_populations = populations
    return _ok(row, f"Default populations set: '{populations}'")


def insert_chart(ctx: AssemblyContext, row: dict, settings: dict) -> dict:
    """
    Render a Base Chart from cached data and insert it at the placeholder position.

    All sub-steps — loading the data shape, rendering the chart image,
    sizing the image to fit the placeholder, inserting via python-pptx —
    are internal to this function and exist solely to accomplish the insertion.
    """
    if ctx.prs is None:
        return _err(row, "insert_chart: no open presentation (create_ppt not called?).")

    cache_file = str(row.get("cache_file") or "").strip()
    if cache_file.lower() == "none":
        cache_file = ""
    chart_type_ref = str(row.get("chart_type_ref", "")).strip()
    slide_index = _int_or_none(row.get("slide_index"))
    placeholder = str(row.get("placeholder", "")).strip()

    # Position / size from the Running Order row (written from template at generation time)
    left_emu = _int_or_none(row.get("left_emu"))
    top_emu = _int_or_none(row.get("top_emu"))
    width_emu = _int_or_none(row.get("width_emu"))
    height_emu = _int_or_none(row.get("height_emu"))

    # Validate required fields
    missing = []
    if not cache_file:  missing.append("cache_file")
    if not chart_type_ref: missing.append("chart_type_ref")
    if slide_index is None: missing.append("slide_index")
    if None in (left_emu, top_emu, width_emu, height_emu):
        missing.append("position/size EMU values")
    if missing:
        return _err(row, f"insert_chart: missing required fields: {', '.join(missing)}")

    # --- Resolve populations for this chart ---
    row_populations = str(row.get("populations", "") or "").strip()
    populations_str = row_populations if row_populations else ctx.default_populations

    render_context = ctx.report_context

    # --- Load data shape ---
    try:
        data_shape, shape_type = _load_chart_data(cache_file, settings.get("workfile_state"))
    except Exception as e:
        return _err(row, f"insert_chart: failed to load cache '{cache_file}': {e}")

    # --- Build population shapes ---
    population_shapes = []
    if render_context is not None and populations_str:
        workfile_state = settings.get("workfile_state")
        submissions = workfile_state.submissions
        try:
            population_shapes = build_population_shapes(
                data_shape, populations_str, submissions, render_context
            )
        except Exception as e:
            return _err(row, f"insert_chart: failed to build population shapes: {e}")

    # Fall back to full unfiltered shape if no populations resolved
    if not population_shapes:
        from modules.m04_data_shapes.shapes import PopulationShape
        population_shapes = [PopulationShape(role="All", label="All", shape=data_shape)]

    # --- Render chart image ---
    try:
        image_bytes, autotable_stats = _render_chart_image(
            chart_type_ref, population_shapes, width_emu, height_emu, render_context
        )
    except Exception as e:
        return _err(row, f"insert_chart: render failed for '{chart_type_ref}': {e}")

    # Store autotable stats keyed by placeholder name
    ctx.autotable_stats[placeholder] = autotable_stats

    # --- Insert into slide ---
    try:
        _insert_image_at_position(
            ctx.prs, slide_index,
            image_bytes, left_emu, top_emu, width_emu, height_emu
        )
    except Exception as e:
        return _err(row, f"insert_chart: failed to insert image on slide {slide_index}: {e}")

    return _ok(row, f"Chart '{chart_type_ref}' inserted at '{placeholder}' (slide {slide_index + 1})")


def update_text(ctx: AssemblyContext, row: dict, settings: dict) -> dict:
    """
    Replace all flag tokens in the presentation with values for the current reporting unit.

    Tokens replaced:
        [selected-reporting-unit-name]  →  submission_name from ReportContext

    PowerPoint XML splits a single visible string across multiple <a:r> runs at
    arbitrary points (spell-check boundaries, autocorrect, manual edits). A run-by-run
    replace will silently miss any token that spans a run boundary. This implementation
    works at the paragraph level via lxml: it collapses all run text into the first run,
    does the replacement there, then clears the remaining runs — preserving the
    formatting of the first run throughout.
    """
    if ctx.prs is None:
        return _err(row, "update_text: no open presentation (create_ppt not called?).")

    rc = ctx.report_context
    tokens = {}
    if rc:
        tokens["[selected-reporting-unit-name]"] = rc.submission_name or ""

    if not tokens:
        return _ok(row, "update_text: no tokens to replace (no ReportContext).")

    # XML namespace for DrawingML text runs
    _nsmap = "a"
    _run_tag = "{http://schemas.openxmlformats.org/drawingml/2006/main}r"
    _t_tag   = "{http://schemas.openxmlformats.org/drawingml/2006/main}t"

    replacements = 0

    for slide in ctx.prs.slides:
        for shape in slide.shapes:
            if not shape.has_text_frame:
                continue
            for para in shape.text_frame.paragraphs:
                runs = para.runs
                if not runs:
                    continue

                # Check whether the full paragraph text contains any token
                full_text = "".join(r.text for r in runs)
                needs_replace = any(tok in full_text for tok in tokens)
                if not needs_replace:
                    continue

                # Apply all token replacements to the full paragraph text
                replaced = full_text
                for token, value in tokens.items():
                    if token in replaced:
                        replaced = replaced.replace(token, value)
                        replacements += 1

                # Write the replaced text into the first run's <a:t> element,
                # then delete all subsequent runs from the paragraph XML.
                first_run_xml = runs[0]._r        # lxml element for the run
                t_elem = first_run_xml.find(_t_tag)
                if t_elem is not None:
                    t_elem.text = replaced

                # Remove every run element after the first from the paragraph XML
                para_xml = para._p
                run_elements = para_xml.findall(_run_tag)
                for run_elem in run_elements[1:]:
                    para_xml.remove(run_elem)

    return _ok(row, f"update_text: {replacements} replacement(s) made.")


def empty_placeholder(ctx: AssemblyContext, row: dict, settings: dict) -> dict:
    """No-op. Placeholder has no content assigned."""
    ph = row.get("placeholder", "")
    return _ok(row, f"empty_placeholder: '{ph}' skipped (no content assigned)")


def save_ppt(ctx: AssemblyContext, row: dict, settings: dict) -> dict:
    """Save the completed output as a .pptx file."""
    if ctx.prs is None:
        return _err(row, "save_ppt: no open presentation.")
    try:
        os.makedirs(os.path.dirname(ctx.output_path), exist_ok=True)
        ctx.prs.save(ctx.output_path)
        return _ok(row, f"Saved: {ctx.output_path}")
    except Exception as e:
        return _err(row, f"save_ppt: {e}")


def save_pdf(ctx: AssemblyContext, row: dict, settings: dict) -> dict:
    """
    Save the completed output as a .pdf using COM automation (Windows/PowerPoint only).
    Falls back gracefully on non-Windows or if PowerPoint is not available.
    """
    if ctx.prs is None:
        return _err(row, "save_pdf: no open presentation.")

    pdf_dir = os.path.join(os.path.dirname(os.path.dirname(ctx.output_path)), "pdf")
    pdf_path = os.path.join(pdf_dir, os.path.basename(ctx.output_path).replace(".pptx", ".pdf"))
    os.makedirs(pdf_dir, exist_ok=True)

    # Ensure the pptx is saved first (COM needs a file on disk to open)
    try:
        ctx.prs.save(ctx.output_path)
    except Exception as e:
        return _err(row, f"save_pdf: could not save .pptx before PDF export: {e}")

    try:
        import comtypes.client
        powerpoint = comtypes.client.CreateObject("Powerpoint.Application")
        powerpoint.Visible = 1
        deck = powerpoint.Presentations.Open(os.path.abspath(ctx.output_path))
        deck.ExportAsFixedFormat(
                os.path.abspath(pdf_path),
                2,   # ppFixedFormatTypePDF
                2,   # Intent: ppFixedFormatIntentPrint (vs 1 = screen quality)
            )
        deck.Close()
        powerpoint.Quit()
        return _ok(row, f"PDF saved: {pdf_path}")
    except ImportError:
        return _err(row, "save_pdf: comtypes not available — PDF export requires Windows + PowerPoint.")
    except Exception as e:
        return _err(row, f"save_pdf: COM export failed: {e}")


# ---------------------------------------------------------------------------
# Dispatch map  —  function name -> callable
# ---------------------------------------------------------------------------

FUNCTION_MAP = {
    "create_ppt":               create_ppt,
    "set_default_populations":  set_default_populations,
    "insert_chart":             insert_chart,
    "insert_picture":           insert_picture,
    "insert_from_excel":        insert_from_excel,
    "open_excel":               open_excel,
    "close_excel":              close_excel,
    "update_text":              update_text,
    "empty_placeholder":        empty_placeholder,
    "save_ppt":                 save_ppt,
    "save_pdf":                 save_pdf,
}


# ---------------------------------------------------------------------------
# Run a complete Running Order
# ---------------------------------------------------------------------------

def run_running_order(rows: list[dict], settings: dict,
                      on_progress=None, ctx: AssemblyContext = None) -> dict:
    """
    Execute a list of Running Order rows (already filtered to enabled only).

    settings dict must contain at minimum:
      ppt_template_path      path to the original template
      cleaned_template_path  path to the cleaned template (yellow boxes removed)
      workfile_folder        root folder; outputs/ subfolder is created here
      reporting_unit_name    used to name the output file
      workfile_state         the open WorkfileState — submissions and cache are
                              always read from here, never from disk

    ctx: optional existing AssemblyContext — pass a shared context from the
         Batch Controller so that batch_open state (e.g. open Excel workbooks)
         persists across reports. If None, a fresh context is created.

    on_progress: optional callback(row_index, total_rows, message)

    Returns:
    {
        "status":   "ok" | "error",
        "output_path": str,
        "elapsed":  float,
        "log":      list[dict],   # one entry per row
    }
    """
    # Use a shared context if provided (batch run), otherwise create a fresh one.
    # A shared context carries open Excel workbook references across reports.
    if ctx is None:
        ctx = AssemblyContext()

    # Build ReportContext from the passed-in settings (which carry per-unit overrides
    # during batch runs) rather than re-reading from disk.
    workfile_state = settings.get("workfile_state")
    submissions = workfile_state.submissions
    ctx.report_context = build_report_context(settings, submissions)

    t_start = time.perf_counter()

    # Only run normal-scoped rows — batch_open and batch_close are the
    # Batch Controller's responsibility and are never passed here.
    normal_rows = [r for r in rows if str(r.get("scope", "normal")).strip() == "normal"]
    rows_to_run = normal_rows

    total = len(rows_to_run)

    for i, row in enumerate(rows_to_run):
        func_name = str(row.get("function", "")).strip()

        if on_progress:
            on_progress(i + 1, total, f"Row {row.get('row_id', i+1)}: {func_name}")

        func = FUNCTION_MAP.get(func_name)
        if func is None:
            result = _err(row, f"Unknown function: '{func_name}'")
        else:
            try:
                result = func(ctx, row, settings)
            except Exception as e:
                result = _err(row, f"Unhandled exception in '{func_name}': {traceback.format_exc()}")

        ctx.log.append(result)

        # Abort on error in structural functions
        if result["status"] == "error" and func_name in ("create_ppt",):
            ctx.log.append({"status": "aborted",
                            "message": "Batch aborted after create_ppt failure."})
            break

    elapsed = time.perf_counter() - t_start
    overall_status = "ok" if all(r["status"] in ("ok", "skip") for r in ctx.log) else "error"

    return {
        "status": overall_status,
        "output_path": ctx.output_path,
        "elapsed": elapsed,
        "log": ctx.log,
    }


# ---------------------------------------------------------------------------
# Private helpers — internal to insert_chart sub-steps
# ---------------------------------------------------------------------------

def _load_chart_data(cache_file: str, workfile_state=None):
    """Load a canonical data shape from the cache. Sub-step of insert_chart."""
    return load_shape(cache_file, workfile_state)


def _render_chart_image(chart_type_ref: str, population_shapes: list, width_emu: int, height_emu: int,
                        report_context=None):
    """
    Render a Matplotlib chart to PNG bytes sized to the placeholder.
    Sub-step of insert_chart.
    """
    NARROWER_EMU = 6858000
    width_pct  = max(10, int(min(100, (width_emu  / NARROWER_EMU) * 100)))
    height_pct = max(10, int(min(100, (height_emu / NARROWER_EMU) * 100)))

    image_bytes, autotable_stats = render_chart(
        chart_type_ref, population_shapes,
        width=width_pct, height=height_pct,
        report_context=report_context,
    )
    return image_bytes, autotable_stats


def _insert_image_at_position(prs: Presentation, slide_index: int,
                               image_bytes, left_emu: int, top_emu: int,
                               width_emu: int, height_emu: int):
    """
    Insert a PNG image at the exact EMU position on the given slide.
    Sub-step of insert_chart.
    """
    if slide_index >= len(prs.slides):
        raise IndexError(
            f"Slide index {slide_index} out of range "
            f"(template has {len(prs.slides)} slides)."
        )
    slide = prs.slides[slide_index]
    image_bytes.seek(0)
    slide.shapes.add_picture(
        image_bytes,
        Emu(left_emu), Emu(top_emu),
        Emu(width_emu), Emu(height_emu),
    )


# ---------------------------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------------------------

def _ensure_output_folder(settings: dict) -> str:
    output_folder = settings.get("outputs_folder", "").strip()
    if not output_folder:
        workfile_folder = settings.get("workfile_folder", "").strip()
        output_folder = os.path.join(workfile_folder, "outputs") if workfile_folder else "outputs"
    os.makedirs(output_folder, exist_ok=True)
    return output_folder


def _safe_filename(name: str) -> str:
    """Strip characters that are unsafe in filenames."""
    import re
    safe = re.sub(r'[\\/:*?"<>|]', "_", name)
    return safe.strip("_") or "output"


def _int_or_none(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _ok(row: dict, message: str) -> dict:
    return {
        "status": "ok",
        "row_id": row.get("row_id", ""),
        "function": row.get("function", ""),
        "message": message,
    }


def _err(row: dict, message: str) -> dict:
    return {
        "status": "error",
        "row_id": row.get("row_id", ""),
        "function": row.get("function", ""),
        "message": message,
    }
