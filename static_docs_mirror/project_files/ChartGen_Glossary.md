# ChartGen — Glossary (DRAFT — restructured, for review)

*Working draft, restructured from the original Glossary.*

---

## Module Map

Top-level structure only. See Architecture, Sections 3–4, for descriptions.

```
Software Domain
chartgen/
├── app.py
├── run_chartgen.bat
├── requirements.txt
├── user_resources/
└── modules/
    ├── m01_data_acquisition/
    ├── m02_template_reader/
    ├── m03_running_order/
    ├── m04_data_shapes/
    ├── m05_chart_engine/
    ├── m06_assembly_engine/
    ├── m07_insert_picture/
    ├── m08_insert_from_excel/
    ├── m09_static_config/
    ├── m10_project_config/
    ├── m11_data_cache/
    ├── m12_local_config/
    └── m14_project_file/

Project Domain (.cgp)
MyProject.cgp  (ZIP)
├── project_config/
├── data_cache/
├── template/
└── project_info.json
```

---

## Business & Reporting Domain

### Comparative analysis domain

- **Normalisation** — bringing data from different sources into a single, consistent structure and format. See the Primer, Section 3; see also Data shape.

- **Peer group** — a named subset of the population. See Functional Spec, Section 7.2, for the `Name()` column mechanism.

- **Population** — the set of units being compared. A single output may include analysis of multiple different populations, usually in a hierarchical relationship (e.g. Regions, Organisations, and Emergency Departments). See the Primer, Section 3.

- **Selected unit(s)** — the unit or units that are the current focus of a comparative analysis, examined in the context of the wider population they sit within. May also be the reporting unit, but does not have to be. E.g. a report for an organisation could have a chart where an Emergency Department is the selected unit.

- **Summary statistics** — numeric values describing a population's data (e.g. mean, median, quartiles, peer averages). See also Autotable.

- **Unit** — a single organisation or entity being compared against others within a population. Will often, but not always match to project submissions. Reporting unit is the named special case used for the organisation an output is being generated for. See the Primer, Section 3.

### ChartGen scope & reporting

- **Algorithmic Report** — a report whose structure itself varies per unit based on conditional logic, not just the data within a fixed structure.

- **Bespoke Narrative** — per-unit written narrative generated for each report. This could be a lookup of human written narrative, algorithmically selected, AI generated, or a combination of these or other approaches.

- **Individualised Report** — a report with a fixed structure, but data varying per instance.

- **Output** — a generated PowerPoint or PDF deliverable produced by ChartGen. Preferred over "report" where possible, as it also includes slide packs, fliers, and presentations.

- **Project** (TBN usage) — a single benchmarking exercise with its own data collection, population, and reporting cycle, identified by a `project_id` and `year`. TBN consistently uses "project," not "programme," for this concept.

- **Reporting unit** — the individual unit (typically an organisation or site) that an output is being generated for; a named special case of Unit.

---

## ChartGen System & Architecture Terms

### Cluster 4 — File & session structure

- **`.cgp`** — ChartGen Project file. A ZIP archive containing all of one project's saved state. See the Architecture document, Section 4, for full internal structure.

- **Data Cache** — the physical, on-disk store of fetched chart data: `data_cache/manifest.json` and one JSON file per chart shape dataset, inside the `.cgp`. Constitutes the data side of the Project domain when the file is closed. Mirrored in memory by `ProjectState.cache`/`.manifest` while the project is open.

- **ProjectState** — the in-memory Python object holding the complete working state of an open `.cgp`. The sole interface other modules use to read or write project data during a session. See the Architecture document, Section 5.

### Cluster 5 — Template & placeholders

- **Cleaned template** — the version of a `.pptx` template with all yellow annotation textboxes stripped out. The Assembly Engine always runs from this version, never the original marked-up template.

- **Placeholder** — a named PowerPoint placeholder that the Running Order references by name for content insertion.

- **Yellow textbox convention** — the template-authoring method of placing a yellow-filled textbox inside a placeholder to associate it with a data source (URL), image path, or Excel range.

### Cluster 6 — TBN Toolkit structures

- **Denominator (TBN Toolkit)** — a variable and URL component that enables webpages to include multiple data sources/calculations. Most commonly used to vary the denominator value, but can change numerators and calculations as well.

- **Service (TBN Toolkit)** — part of the TBN project process enabling multiple questionnaires per project. A URL component.

- **Tier (TBN Toolkit)** — a component of the toolkit structure which hosts charts.

### Cluster 7 — Data shapes & populations

- **Chart data** — a comparative dataset for a specific analysis. Called "chart data" because it typically originates from a chart fetch and ends up rendered in a chart, but the data itself is agnostic to that flow and could be, for example, used in tables.

- **Data shape** — a data container for normalised chart data. See Functional Spec, Section 8.

- **Population shape (`PopulationShape`)** — one filtered, stats-recalculated copy of a data shape representing a single population layer (e.g. "all units," "Welsh units," "the selected unit"), produced by `build_population_shapes` and consumed by chart rendering. See Functional Spec, Section 10.4, and the Architecture document, Section 5.

- **Populations string** — the `^`-delimited ordered list of tokens (e.g. `All^Region()^Selected`) that specifies which population shapes are sent to the chart engine. See Functional Spec, Section 10.4.

### Cluster 8 — Running Order & execution

- **Batch** — processing multiple outputs in a single run.

- **Enabled column** — the per-row on/off switch in the Running Order. Stored as an integer `1`/`0` at runtime.

- **Flag token** — a placeholder string embedded in template text (e.g. `[selected-reporting-unit-name]`) replaced with a per-unit value at generation time by `update_text`.

- **Running Order** — the user-authored, row-based instruction table that defines report assembly: function, parameters, control flag. See Functional Spec, Section 9, and the Architecture document, Decision 1, for storage format.

- **Scope (`normal` / `batch_open` / `batch_close`)** — the Running Order column controlling when a row executes relative to a batch: once per report (`normal`), once before the whole batch (`batch_open`, e.g. `open_excel`), or once after (`batch_close`, e.g. `close_excel`).

### Cluster 9 — Runtime objects

- **AssemblyContext** — the in-memory object the Assembly Engine builds once per batch run, carrying the open `Presentation` object, output path, run log, autotable stats, the current `ReportContext`, default populations string, and any open Excel COM workbook references. See the Architecture document, Section 5.

- **Item table** — the submissions-based table the user interacts with to select a reporting unit and inspect populations; built from `submissions.csv`.

- **ReportContext** — the per-report identity object (`submission_id`, `submission_code`, `submission_name`, `organisation_id`, `organisation_name`), rebuilt fresh for each submission in a batch run and passed to chart rendering and text replacement.

- **Submission / submission ID / submission code** — a single reporting unit's data record for a project. `submission_id` is the internal numeric identifier; `submission_code` is the outward-facing label (used for display only, never relied on for logic); `submission_name` is the display name (e.g. Trust name).

### Cluster 10 — Chart construction

- **Autotable** — a table populated from statistics computed as a byproduct of chart construction (mean, quartiles, peer averages, and the value(s) for the selected unit(s)), rather than from flag token replacement. Distinct from flag-based tables.

- **Base Chart** — one of ChartGen's chart-rendering functions, each handling one canonical data shape.

- **Tweak** — a chart-rendering customisation (reference lines, axis control, conditional colouring, etc.)

### Cluster 11 — Excel integration

- **Driver range / export range** — Excel named ranges used by `insert_from_excel`: the driver range receives the current `submission_id`; the export range is the area captured as an image afterwards.
