# ChartGen — Architecture

*TBN Internal · Input document for refactoring — describes the current system only*

---

## 1. Purpose and Scope

Describes how ChartGen is built: its structure, the format of its data at rest and in memory, and the technical decisions that govern it.

---

## 2. Two Domains

ChartGen's data exists in two separate places, each with its own lifecycle, format, and rules about what may live there.

| Domain | What it is | Lifecycle | Format |
|---|---|---|---|
| **Software** | The installed application — code, static config, per-machine settings | Persists across every project and session until reinstalled or updated | Python source, CSV (static config), one small per-machine CSV (username) |
| **Workfile** | A single workfile's complete footprint — the `.cgw` file, its sibling `.pptx` and `outputs/` folder, and, while open, the in-memory working copy of all of it | The `.cgw`/`.pptx`/`outputs/` persist once saved and are shareable; the in-memory copy exists only between Open and Close/crash, discarded if not saved | `.cgw` (ZIP), sibling `.pptx` and `outputs/` folder on disk; Python objects — dataclasses, dicts, lists — in memory when open |

Memory isn't a third place workfile data lives — it's the Workfile domain's in-session form, the working copy of what's on disk. It gets its own walkthrough below (Section 5) because its structure differs enough from the on-disk layout to warrant one, not because it's conceptually separate.

**Defining rule:** the Software domain doesn't change as a result of workfile work. Opening a workfile, fetching data, editing the Running Order, running batches — none of it touches the installed application, the same way writing a letter in Word doesn't change Word itself. The Software domain changes only as a function of *which user is logged in on this machine*, never as a function of *what workfile work was done*. The one exception (last-used username) is documented under Decision 7.

---

## 3. Software Domain

The installed application folder. Identical on every machine running the same version of ChartGen; never contains workfile data.

```
chartgen/
├── app.py
├── run_chartgen.bat
├── requirements.txt
├── user_resources/
│   └── PPT_Template_Creation.md
└── packages/
    ├── data_acquisition/
    ├── template_reader/
    ├── running_order/
    ├── data_shapes/
    ├── chart_engine/
    ├── assembly_engine/
    ├── insert_picture/
    ├── insert_from_excel/
    ├── static_config/
    │   └── chart_type_map.csv
    ├── local_config/
    │   ├── local_config.py
    │   └── credentials.csv
    └── workfile_file/
        └── workfile_file.py
```

| Path | Notes |
|---|---|
| `app.py` | Streamlit entry point — UI, sidebar, tabs |
| `run_chartgen.bat` | Double-click launcher; creates venv on first run |
| `requirements.txt` | Python dependencies (kept in sync with `.bat`) |
| `user_resources/PPT_Template_Creation.md` | Guidance doc for template designers |
| `packages/data_acquisition/` | Fetch → canonical data shapes (API client, transformers) |
| `packages/template_reader/` | Reads `.pptx` placeholders; detects/strips yellow boxes |
| `packages/running_order/` | Running Order schema, xlsx import/export (transient only) |
| `packages/data_shapes/` | NumericSeries / NumericCompositional / CategoricalCompositional |
| `packages/chart_engine/` | 17 Base Charts; `render_chart` dispatch |
| `packages/assembly_engine/` | Running Order executor — the only package touching `python-pptx` |
| `packages/insert_picture/` | `insert_picture` Running Order function |
| `packages/insert_from_excel/` | Excel COM capture (`open_excel` / `insert_from_excel` / `close_excel`) |
| `packages/static_config/chart_type_map.csv` | Data shape → valid chart type refs (developer-owned, read-only) |
| `packages/local_config/local_config.py` | `ReportContext` + `build_report_context()` |
| `packages/local_config/credentials.csv` | Last-used username only, rewritten every login — ★ the one genuine exception to the software/workfile split, see Decision 7 |
| `packages/workfile_file/workfile_file.py` | Owns the `.cgw` format — see Section 4. The only module that reads/writes the ZIP directly |

---

## 4. Workfile Domain — On Disk (`.cgw`)

A single workfile's complete, portable, shareable state. Internally a ZIP archive — the same pattern as `.pptx`, `.docx`, `.xlsx`.

```
MyWorkfile.cgw  (ZIP)
├── workfile_config/
│   ├── settings.csv
│   ├── urls.csv
│   ├── units.csv
│   └── running_order.csv
├── data_cache/
│   ├── manifest.json
│   └── {tier_id}_{group}_{option}.json
├── template/
│   └── MyWorkfile.pptx
└── workfile_info.json
```

| Path | Notes |
|---|---|
| `workfile_config/settings.csv` | key,value — paths, year, project_id, batch_cursor, etc. |
| `workfile_config/urls.csv` | Toolkit URLs (populated by yellow-box extraction) |
| `workfile_config/units.csv` | Population table — one row per reporting unit, `Region()` column |
| `workfile_config/running_order.csv` | ★ Canonical Running Order store — flat table, not `.xlsx`. The `.xlsx` is generated from this on demand for download and parsed back into it on upload; it is never itself written to this archive |
| `data_cache/manifest.json` | Index: tier_id, group, option, label, shape_type, url, last_fetched — per cached chart |
| `data_cache/{tier_id}_{group}_{option}.json` | One file per fetched chart — serialised data shape |
| `template/MyWorkfile.pptx` | Reference copy of the cleaned template — validation only. Never run from. Compared against the live sibling `.pptx` (below) to warn on structural drift |
| `workfile_info.json` | Stored uncompressed (`ZIP_STORED`) — cheap to read alone, before the rest of the archive loads. Contains `workfile_name`, `last_saved_by`, `last_saved_at`, `chartgen_version`, `locked_by` (advisory concurrency), `locked_at` (see Decision 4) |

**Running Order column schema** (`running_order.csv`):

| Column | Description |
|--------|-------------|
| `row_id` | Unique integer row identifier (1-based) |
| `enabled` | 1 / 0 — disabled rows are skipped at runtime |
| `scope` | `normal` / `batch_open` / `batch_close` — when the row executes relative to a batch |
| `function` | Function name to call |
| `slide_index` | 0-based slide index (blank for structural functions) |
| `placeholder` | Placeholder name, e.g. `Chart 1` (blank for structural functions) |
| `chart_type_ref` | Base Chart function name, e.g. `ranked_column` (blank for non-chart rows) |
| `cache_file` | JSON cache filename supplying data for this chart (blank for non-chart rows) |
| `populations` | Per-row populations string, overriding the project default (blank to use the default) |
| `image_path` | Source image path for `insert_picture`; may contain `[code]`/`[id]` tokens |
| `excel_path` | Workbook path for `open_excel` / `insert_from_excel` / `close_excel` |
| `export_range` | Excel named range captured as an image by `insert_from_excel` |
| `driver_range` | Excel named range receiving the current `unit_id` |
| `left_emu` | Left position in EMU — populated from template |
| `top_emu` | Top position in EMU — populated from template |
| `width_emu` | Width in EMU — populated from template |
| `height_emu` | Height in EMU — populated from template |
| `notes` | Free text; user reference only, ignored at runtime |

**Sitting alongside the `.cgw`, not inside it** — these are the only other artefacts a colleague sees on a shared drive:

```
MyWorkfile.pptx
outputs/
  pptx/
  pdf/
```

| Path | Notes |
|---|---|
| `MyWorkfile.pptx` | Cleaned template, user-owned and editable — Decision 2. A separate, real file rather than something buried in the ZIP |
| `outputs/pptx/` | Generated `.pptx` reports, one per batch run output. Recreated fresh wherever the `.cgw` currently lives, including after a Save As — not carried across |
| `outputs/pdf/` | Generated `.pdf` reports. Recreated fresh wherever the `.cgw` currently lives, including after a Save As — not carried across |

**CSV vs JSON.** `running_order.csv`, `units.csv`: flat, fixed-column, one-row-per-entity — CSV's natural shape, and legible to a non-technical colleague who renames `.cgw` to `.zip`. `data_cache/*.json`: nested (serialised dataclasses), never hand-edited. Intentional split, not an inconsistency.

---

## 5. Workfile Domain — In Memory (Runtime)

What exists only while the application is running, for the duration of one open session. Built and discarded; never written to disk except via the explicit Save action (the Workfile domain's on-disk form) or the explicit `save_ppt`/`save_pdf` Running Order functions (their own output, not this domain's own state).

```
Streamlit process (st.session_state)
├── st.session_state["ws"] → WorkfileState
│     workfile_path, workfile_name
│     settings: dict
│     urls: list[dict]
│     units: list[dict]
│     running_order_rows: list[dict]
│     manifest: dict
│     cache: dict — {filename: json_string}
│     template_pptx_bytes: bytes | None
│     last_saved_by
│     last_saved_at
│     locked_by
│     locked_at
│     dirty: bool
│     read_only: bool
│
├── st.session_state["token"]
├── st.session_state[...UI flags...]
│
└── Per-batch-run objects
    ├── AssemblyContext
    │     prs: Presentation
    │     output_path: str
    │     template_path: str
    │     log: list[dict]
    │     autotable_stats: dict
    │     report_context: ReportContext
    │     default_populations: str
    │     excel_workbooks: dict
    │
    ├── ReportContext
    │     unit_id: int
    │     unit_code: str
    │     unit_name: str
    │     organisation_id: str
    │     organisation_name: str
    │
    └── list[NumericSeries | NumericCompositional | CategoricalCompositional]
          population_label: str  — set per layer by build_population_shapes
```

| Item | Notes |
|---|---|
| `st.session_state["ws"]` → `WorkfileState` | ★ The working copy of the open `.cgw` |
| `WorkfileState.settings: dict` | Mirrors `workfile_config/settings.csv` |
| `WorkfileState.running_order_rows: list[dict]` | ★ Sole live copy — see Section 4 note |
| `WorkfileState.manifest: dict` | Mirrors `data_cache/manifest.json` |
| `WorkfileState.cache: dict` — `{filename: json_string}` | Mirrors `data_cache/*.json` |
| `WorkfileState.dirty: bool` | Not persisted — session-only flag |
| `WorkfileState.read_only: bool` | Not persisted — session-only. True only for a session opened via Open Read-Only; such a session never writes or clears the lock. |
| `st.session_state["token"]` | API session token (Decision 7) — never the password |
| `st.session_state[...UI flags...]` | `show_new_form`, `ro_selected_idx`, etc. — disposable, no domain meaning beyond this widget render |
| Per-batch-run objects | Live only for the duration of one Run Selected / Run Batch / Run All call — constructed fresh, discarded after |
| `AssemblyContext` | One per **batch** (persists across reports within it) |
| `AssemblyContext.report_context: ReportContext` | Rebuilt per report, see below |
| `AssemblyContext.excel_workbooks: dict` | Added dynamically by `open_excel`, Insert From Excel |
| `ReportContext` | One per **report** (rebuilt fresh per unit, from the per-report settings dict, never from `load_settings()` — batch overrides apply correctly) |
| `list[data shape]` | One list per `insert_chart` call — built fresh by `build_population_shapes()` each time; each entry is a filtered copy of the chart's data shape, stats recalculated |
| `population_label: str` | Field on the data shape itself — e.g. `"All"`, `"Selected"`, or a resolved peer-group value |

Only `WorkfileState` (Decision 1) holds real state. `AssemblyContext`, `ReportContext`, and population-filtered data shape lists are just rebuilt from it on every run, the way any app rebuilds working objects from its underlying data rather than treating them as sources of truth in their own right. If the Streamlit process dies mid-session, everything here is gone except whatever was already saved.

---

## 6. Design Decisions

### Decision 1 — Workfile File Format (`.cgw`)

ChartGen workfiles are saved as a single `.cgw` file — internally a ZIP archive, the same pattern as `.pptx`, `.docx`, and `.xlsx`. The extension signals to Windows that the file belongs to ChartGen. Full internal structure in Section 4.

The Running Order's canonical store is `running_order.csv` inside the `.cgw` — a flat table, not xlsx. The `.xlsx` is a human-facing export/import format only, never itself stored in the workfile.

All working state during a session lives in the in-memory `WorkfileState` object, not on disk (Section 5) — the same convention as Word, Excel, and PowerPoint. `WorkfileState` is owned and managed exclusively by `workfile_file`; no other package touches the ZIP directly.

**Memory footprint.** All workfiles are structured text (CSV, JSON). Chart data — the largest component — runs to approximately 50–100KB per chart. A large workfile with 200 charts holds under 20MB in memory. Not a concern.

**Rationale.** Same working pattern as common MS Office applications.

### Decision 2 — Cleaned Template Asset

The cleaned template (yellow textboxes stripped) is saved as a named `.pptx` file alongside the workfile, with an identical base name (see Section 4 for the layout). The user owns `MyWorkfile.pptx` — they may open it directly in PowerPoint and edit it. ChartGen always runs from this file.

**Two edit tiers.** *Cosmetic edits* (text, colours, fonts, non-placeholder shapes) — the user edits `MyWorkfile.pptx` directly; ChartGen picks it up silently on the next run, no reprocessing needed. *Structural edits* (slides added/removed, placeholders moved/renamed, new yellow boxes) — the user edits the original marked-up template and re-uploads it; this overwrites `MyWorkfile.pptx` and the reference copy inside the `.cgw`, and regenerates the Running Order.

Outputs are written to `outputs/pptx/` and `outputs/pdf/` alongside the workfile, created automatically on first run.

### Decision 3 — Template Validation

A reference copy of the cleaned template is stored inside the `.cgw` (`template/MyWorkfile.pptx`) at the point of processing. This copy is never run from — it exists solely for validation.

**Validation at run time.** ChartGen extracts the ordered list of slide layout names from both the reference copy (inside `.cgw`) and the live asset (`MyWorkfile.pptx` alongside the workfile). Matching lists — proceed silently. Differing lists — surface a specific, actionable warning naming exactly which slides changed and how. The warning is soft; the user can proceed or reprocess.

**Why layout names, not slide count.** Layout name comparison catches slides added, removed, reordered, or with a swapped layout — all of which affect placeholder positions and indices in the Running Order. It does not warn for cosmetic edits within a slide, which is correct — those edits are intentional and safe.

### Decision 4 — `workfile_info.json` (Metadata and Concurrency)

Sits in the root of the `.cgw`, stored uncompressed (`ZIP_STORED`), so it can be read from the ZIP by name, without loading the full archive, cheaply at Open time, before `WorkfileState` is fully loaded.

Serves two purposes: session metadata (audit trail, sidebar display) and concurrency signalling (soft lock). Contents shown in Section 4.

`locked_by`/`locked_at` are written when a user opens the workfile and cleared when they close it. When `locked_by` is present, the user opening the file sees an advisory decision step naming the holder and the time — they can choose to open normally or open Read-Only. A hard block is not appropriate, since the lock may be stale (crash, force-quit) with no automatic way to distinguish a live lock from an orphaned one.

**Why inside the ZIP, not a sibling file.** A sibling lock file would be visible on SharePoint as a separate item, and a source of confusion for colleagues. The lock fields inside `workfile_info.json` are invisible to anyone not opening the workfile in ChartGen — the right audience for the warning.

Lock behaviour for each sidebar operation, and for a crash, is in Decision 6.

### Decision 5 — Concurrency

Managed entirely via the lock fields in Decision 4 — no external lock file.

The model is advisory: opening a workfile always shows a decision step (Decision 6) naming the lock state, if any, and offering Open or Open Read-Only. Open Read-Only proceeds without claiming the lock. Last-write-wins applies if two users choose Open and both save — acceptable for a small team with normal verbal coordination. A hard concurrency lock is explicitly out of scope. Per-operation lock behaviour is in Decision 6.

### Decision 6 — File Operations and UI

File operations live in the Streamlit sidebar, tab-agnostic. The main tab interface is only active when a workfile is open; with none loaded, tabs are present but empty.

| Operation | Behaviour |
|---|---|
| **New Workfile** | Prompts for save location and name, then runs the New Workfile flow. Submissions fetch is the final blocking step. |
| **Open Workfile** | File picker for `.cgw`. Always leads to a decision step naming the lock state before the workfile loads, offering Open or Open Read-Only. Open writes the lock; Open Read-Only does not. |
| **Save** | Serialise `WorkfileState` to ZIP, update `workfile_info.json`. No confirmation dialog. Disabled in a Read-Only session. |
| **Save As** | New folder/name via native picker. Copies the cleaned template alongside the new `.cgw` under the matching name; releases the lock on the old file, writes a new one. Outputs are not carried across. In a Read-Only session, the target folder must differ from the original workfile's; on success the session becomes normal, and the old file's lock is released only if this session had held it. |
| **Save and Close** | Save, then clear `locked_by`+`locked_at`, return to no-workfile-loaded state. Disabled in a Read-Only session. |
| **Close Without Saving** | Confirms if dirty. Clears the lock; ZIP otherwise untouched. Skips the confirmation in a Read-Only session — closes immediately regardless of unsaved edits. |

Buttons are active/inactive based on the state of the software.

**Crash.** Lock fields remain as last written. The next user opening the workfile sees the stale lock as the same decision step described above.

**Read-Only sessions.** Offered on every Open regardless of lock state. Enforcement is shallow: Save is disabled; every other action behaves as normal, so unsaved edits are lost unless rescued via Save As. A Read-Only session never writes the lock, and therefore never clears one on close.

### Decision 7 — Credentials Location

Only the username is stored, in `local_config/credentials.csv` — rewritten on every successful login, saving the user from re-entering it on next launch. The password and session token are never persisted to disk; the token lives only in `st.session_state["token"]` for the session's duration.

This is per-machine, per-user data, not workfile data, so it lives in `local_config/` rather than the workfile or static config.

### Decision 8 — SharePoint Compatibility

ChartGen is designed for a SharePoint-hosted team environment accessed via OneDrive sync.

Charts render entirely in memory as bytes; the only disk writes during a batch run are the final `save_ppt`/`save_pdf` calls, one per report. The `.cgw` is read once at the start of a run and not written again until Save. This avoids the small, rapid file writes that trigger OneDrive sync issues, and leaves the sync client nothing to lock mid-run.

Files accessed via OneDrive sync appear as ordinary local filesystem paths to Python — `zipfile`, `open()`, `shutil` all work unmodified. This avoids the filesystem-API incompatibilities that affect COM/VBA approaches against SharePoint's virtual file system.

### Decision 9 — Application Location (Interim)

For the current phase, ChartGen lives in a folder on the C: drive under direct developer control. No installer, no registered file associations yet. File association for `.cgw` and a proper installer (e.g. Inno Setup) are deferred until the application is stable enough to warrant a more professional distribution approach.

---

See the refactor issues document for open items carried forward from this architecture (type coercion, multi-project support, file association, Text Engine/Batch Controller package split).
