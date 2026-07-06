"""
base_charts.py
Base Chart functions — one per chart type reference. Each takes population_shapes, width, height,
tweaks, and report_context, and returns (image_bytes, autotable_stats).
"""

import io
import warnings
warnings.filterwarnings("ignore")

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.ticker as mticker
import matplotlib.colors as mcolors
import numpy as np

import seaborn as sns

from modules.m04_data_shapes.shapes import (
    NumericSeries,
    NumericCompositional,
    CategoricalCompositional,
    PopulationShape,
)

# ---------------------------------------------------------------------------
# Palette
# ---------------------------------------------------------------------------

BAR_BLUE     = "#7CB9E8"
MEAN_COL     = "#E87722"
MEDIAN_COL   = "#4CAF50"
QUARTILE_COL = "#888888"
YES_COL      = "#4CAF50"
NO_COL       = "#C0392B"
NAVY         = "#1F4E79"
ORANGE       = "#E87722"
HIGHLIGHT    = "#C12958"   # TBN crimson — Selected population
PIE_COLOURS  = ["#1F4E79", "#E87722", "#7030A0", "#2E86AB", "#F0A500", "#4CAF50"]
PEER_COLOURS = ["#2E9E75", "#7030A0", "#E87722", "#2E86AB"]  # one per peer group layer

DPI = 300
NARROWER_DIM_INCHES = 7.5


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _size_to_inches(width, height):
    s = NARROWER_DIM_INCHES / 100
    return width * s, height * s


def _fig_to_bytes(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=DPI, bbox_inches="tight",
                facecolor="white", edgecolor="none")
    plt.close(fig)
    buf.seek(0)
    return buf


def _apply_spine_style(ax):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.set_axisbelow(True)


def _k_fmt(v, _):
    return f"{v/1000:.1f}K" if abs(v) >= 1000 else f"{v:g}"


def _layer_colour(pop_index: int, role: str, peer_colour_idx: int) -> str:
    """Return the colour for a population layer given its role and peer index."""
    if role == "Selected":
        return HIGHLIGHT
    if role == "All":
        return BAR_BLUE
    return PEER_COLOURS[peer_colour_idx % len(PEER_COLOURS)]


def _resolve_unit_colours(units: list, population_shapes: list) -> list:
    """Assign a colour to each unit based on which population layer(s) it belongs to."""
    colours = [BAR_BLUE] * len(units)
    peer_colour_idx = 0
    for ps in population_shapes:
        if ps.role == "All":
            continue
        colour = HIGHLIGHT if ps.role == "Selected" else PEER_COLOURS[peer_colour_idx % len(PEER_COLOURS)]
        if ps.role != "Selected":
            peer_colour_idx += 1
        ids = {u.submission_id for u in ps.shape.units}
        for i, u in enumerate(units):
            if u.submission_id in ids:
                colours[i] = colour
    return colours


def _population_legend_handles(population_shapes: list, data_label: str) -> list:
    """Build legend patch handles from population layers."""
    handles = [mpatches.Patch(color=BAR_BLUE, label=data_label)]
    peer_colour_idx = 0
    for ps in population_shapes:
        if ps.role == "All":
            continue
        if ps.role == "Selected":
            handles.append(mpatches.Patch(color=HIGHLIGHT, label="Selected"))
        else:
            colour = PEER_COLOURS[peer_colour_idx % len(PEER_COLOURS)]
            handles.append(mpatches.Patch(color=colour, label=ps.label))
            peer_colour_idx += 1
    return handles


def _get_selected_unit(units: list, report_context) -> tuple:
    """Return (index, value, unit) for the selected submission in a sorted unit list."""
    if report_context is None:
        return None, None, None
    for i, u in enumerate(units):
        if u.submission_id == report_context.submission_id:
            return i, u.values[0], u
    return None, None, None


def _autotable_with_selection(stats: dict, report_context, selected_value) -> dict:
    if report_context is None:
        return stats
    out = dict(stats)
    out["Selected ID"]    = report_context.submission_id
    out["Selected code"]  = report_context.submission_code
    out["Selected name"]  = report_context.submission_name
    out["Selected value"] = round(selected_value, 1) if selected_value is not None else None
    return out


# ===========================================================================
# NUMERIC SERIES
# ===========================================================================

def ranked_column(population_shapes: list, width=80, height=50, tweaks=[], report_context=None):
    """Ranked descending column chart with mean/median/quartile reference lines."""
    base = population_shapes[0].shape
    w, h = _size_to_inches(width, height)
    fig, ax = plt.subplots(figsize=(w, h))
    ms = base.metric_stats[0]
    units = sorted(base.units, key=lambda u: (u.values[0] is None, -(u.values[0] or 0)))
    codes  = [u.submission_code for u in units]
    values = [u.values[0] if u.values[0] is not None else 0 for u in units]
    x = np.arange(len(codes))

    colours = _resolve_unit_colours(units, population_shapes)
    ax.bar(x, values, color=colours, width=0.8, zorder=2)

    sel_idx, sel_val, _ = _get_selected_unit(units, report_context)
    if sel_idx is not None and sel_val is not None:
        ax.annotate(report_context.submission_code,
                    xy=(sel_idx, sel_val), xytext=(0, 6), textcoords="offset points",
                    ha="center", fontsize=7, color=HIGHLIGHT, fontweight="bold")

    if ms.mean   is not None: ax.axhline(ms.mean,   color=MEAN_COL,    linewidth=1.5, zorder=3)
    if ms.median is not None: ax.axhline(ms.median, color=MEDIAN_COL,  linewidth=1.5, zorder=3)
    if ms.q1     is not None: ax.axhline(ms.q1,     color=QUARTILE_COL, linewidth=1, linestyle="--", zorder=3)
    if ms.q3     is not None: ax.axhline(ms.q3,     color=QUARTILE_COL, linewidth=1, linestyle="--", zorder=3)

    ax.set_xticks(x)
    ax.set_xticklabels(codes, rotation=90, fontsize=7)
    ax.set_title(base.title or "", fontsize=10, fontweight="bold", pad=10)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(_k_fmt))
    ax.tick_params(axis="y", labelsize=8)
    ax.yaxis.grid(True, color="#E0E0E0", linewidth=0.7)
    _apply_spine_style(ax)

    label = base.metric_names[0] if base.metric_names else "Value"
    handles = _population_legend_handles(population_shapes, label)
    handles += [
        plt.Line2D([0],[0], color=MEAN_COL,     linewidth=1.5, label="Mean"),
        plt.Line2D([0],[0], color=MEDIAN_COL,   linewidth=1.5, label="Median"),
        plt.Line2D([0],[0], color=QUARTILE_COL, linewidth=1, linestyle="--", label="Lower/Upper Quartiles"),
    ]
    ax.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, -0.28),
              ncol=4, fontsize=7, frameon=False)
    fig.tight_layout()
    stats = {
        "Lower Quartile": round(ms.q1,    1) if ms.q1    is not None else None,
        "Mean":           round(ms.mean,  1) if ms.mean  is not None else None,
        "Median":         round(ms.median,1) if ms.median is not None else None,
        "Upper Quartile": round(ms.q3,    1) if ms.q3    is not None else None,
    }
    return _fig_to_bytes(fig), _autotable_with_selection(stats, report_context, sel_val)


def dot_strip(population_shapes: list, width=80, height=40, tweaks=[], report_context=None):
    """Strip / dot plot — one dot per unit ranked left to right."""
    base = population_shapes[0].shape
    w, h = _size_to_inches(width, height)
    fig, ax = plt.subplots(figsize=(w, h))
    ms = base.metric_stats[0]
    units = sorted(base.units, key=lambda u: (u.values[0] is None, u.values[0] or 0))
    values = [u.values[0] for u in units if u.values[0] is not None]
    x = np.arange(len(values))

    colours = _resolve_unit_colours(units, population_shapes)
    sizes   = [80 if c == HIGHLIGHT else 30 for c in colours]
    ax.scatter(x, values, color=colours, s=sizes, zorder=3, alpha=0.9)

    sel_idx, sel_val, _ = _get_selected_unit(units, report_context)
    if sel_idx is not None and sel_val is not None:
        ax.annotate(report_context.submission_code,
                    xy=(sel_idx, sel_val), xytext=(0, 8), textcoords="offset points",
                    ha="center", fontsize=7, color=HIGHLIGHT, fontweight="bold")

    if ms.mean   is not None: ax.axhline(ms.mean,   color=MEAN_COL,    linewidth=1.5, zorder=2)
    if ms.median is not None: ax.axhline(ms.median, color=MEDIAN_COL,  linewidth=1.5, zorder=2)
    if ms.q1     is not None: ax.axhline(ms.q1,     color=QUARTILE_COL, linewidth=1, linestyle="--", zorder=2)
    if ms.q3     is not None: ax.axhline(ms.q3,     color=QUARTILE_COL, linewidth=1, linestyle="--", zorder=2)
    ax.set_xticks([])
    ax.set_title(base.title or "", fontsize=10, fontweight="bold", pad=10)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(_k_fmt))
    ax.tick_params(axis="y", labelsize=8)
    ax.yaxis.grid(True, color="#E0E0E0", linewidth=0.7)
    _apply_spine_style(ax)
    ax.set_xlabel(f"n = {len(values)} organisations", fontsize=8, color="#555555")

    label = base.metric_names[0] if base.metric_names else "Value"
    handles = _population_legend_handles(population_shapes, label)
    handles += [
        plt.Line2D([0],[0], color=MEAN_COL,     linewidth=1.5, label="Mean"),
        plt.Line2D([0],[0], color=MEDIAN_COL,   linewidth=1.5, label="Median"),
        plt.Line2D([0],[0], color=QUARTILE_COL, linewidth=1, linestyle="--", label="Quartiles"),
    ]
    ax.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, -0.12),
              ncol=4, fontsize=7, frameon=False)
    fig.tight_layout()
    stats = {
        "Lower Quartile": round(ms.q1,    1) if ms.q1    is not None else None,
        "Mean":           round(ms.mean,  1) if ms.mean  is not None else None,
        "Median":         round(ms.median,1) if ms.median is not None else None,
        "Upper Quartile": round(ms.q3,    1) if ms.q3    is not None else None,
    }
    return _fig_to_bytes(fig), _autotable_with_selection(stats, report_context, sel_val)


def box_whisker(population_shapes: list, width=50, height=50, tweaks=[], report_context=None):
    """Box and whisker — distribution from first shape, markers for subsequent layers."""
    base = population_shapes[0].shape
    w, h = _size_to_inches(width, height)
    fig, ax = plt.subplots(figsize=(w, h))
    values = [u.values[0] for u in base.units if u.values[0] is not None]
    ax.boxplot(values, vert=True, patch_artist=True, widths=0.5,
               medianprops=dict(color=MEDIAN_COL, linewidth=2),
               boxprops=dict(facecolor=BAR_BLUE, color=NAVY, linewidth=1.2),
               whiskerprops=dict(color=NAVY, linewidth=1.2),
               capprops=dict(color=NAVY, linewidth=1.2),
               flierprops=dict(marker="o", color=ORANGE, markersize=4, alpha=0.7, markeredgewidth=0))
    ms = base.metric_stats[0]
    if ms.mean is not None:
        ax.axhline(ms.mean, color=MEAN_COL, linewidth=1.5, linestyle="--")

    extra_handles = []
    peer_colour_idx = 0
    for ps in population_shapes[1:]:
        if ps.role == "Selected":
            sel_units = ps.shape.units
            if sel_units and sel_units[0].values[0] is not None:
                sv = sel_units[0].values[0]
                ax.scatter([1], [sv], color=HIGHLIGHT, zorder=7, s=80, marker="D")
                ax.axhline(sv, color=HIGHLIGHT, linewidth=1, linestyle=":", zorder=5, alpha=0.6)
                extra_handles.append(plt.Line2D([0],[0], marker="D", color="w",
                    markerfacecolor=HIGHLIGHT, markersize=7,
                    label=f"{report_context.submission_code}: {sv:g}" if report_context else "Selected"))
        else:
            colour = PEER_COLOURS[peer_colour_idx % len(PEER_COLOURS)]
            peer_colour_idx += 1
            peer_vals = [u.values[0] for u in ps.shape.units if u.values[0] is not None]
            if peer_vals and report_context:
                sel_in_peer = next((u.values[0] for u in ps.shape.units
                                    if u.submission_id == report_context.submission_id
                                    and u.values[0] is not None), None)
                if sel_in_peer is not None:
                    ax.scatter([1], [sel_in_peer], color=colour, zorder=6, s=60, marker="D", alpha=0.85)
                    ax.axhline(sel_in_peer, color=colour, linewidth=0.8, linestyle=":", zorder=5, alpha=0.5)
                    extra_handles.append(plt.Line2D([0],[0], marker="D", color="w",
                        markerfacecolor=colour, markersize=6, label=ps.label))

    ax.set_xticks([])
    ax.set_title(base.title or "", fontsize=10, fontweight="bold", pad=10)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(_k_fmt))
    ax.tick_params(axis="y", labelsize=9)
    ax.yaxis.grid(True, color="#E0E0E0", linewidth=0.7)
    _apply_spine_style(ax)
    ax.set_xlabel(f"n = {len(values)}", fontsize=8, color="#555555")
    handles = [
        mpatches.Patch(facecolor=BAR_BLUE, edgecolor=NAVY, label="IQR"),
        plt.Line2D([0],[0], color=MEDIAN_COL, linewidth=2,
                   label=f"Median: {ms.median:.1f}" if ms.median else "Median"),
        plt.Line2D([0],[0], color=MEAN_COL, linewidth=1.5, linestyle="--",
                   label=f"Mean: {ms.mean:.1f}" if ms.mean else "Mean"),
        plt.Line2D([0],[0], marker="o", color="w", markerfacecolor=ORANGE, markersize=5, label="Outliers"),
    ] + extra_handles
    ax.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, -0.08),
              ncol=2, fontsize=7, frameon=False)
    fig.tight_layout()
    sel_val = next((u.values[0] for ps in population_shapes if ps.role == "Selected"
                    for u in ps.shape.units if u.values[0] is not None), None)
    stats = {
        "Min":            round(ms.min,   1) if ms.min    is not None else None,
        "Lower Quartile": round(ms.q1,    1) if ms.q1     is not None else None,
        "Median":         round(ms.median,1) if ms.median is not None else None,
        "Mean":           round(ms.mean,  1) if ms.mean   is not None else None,
        "Upper Quartile": round(ms.q3,    1) if ms.q3     is not None else None,
        "Max":            round(ms.max,   1) if ms.max    is not None else None,
    }
    return _fig_to_bytes(fig), _autotable_with_selection(stats, report_context, sel_val)


def frequency_histogram(population_shapes: list, width=60, height=45, tweaks=[], report_context=None):
    """Frequency histogram — distribution from first shape, reference lines for subsequent layers."""
    base = population_shapes[0].shape
    w, h = _size_to_inches(width, height)
    fig, ax = plt.subplots(figsize=(w, h))
    values = [u.values[0] for u in base.units if u.values[0] is not None]
    n_bins = min(max(int(np.sqrt(len(values))), 8), 20)
    ax.hist(values, bins=n_bins, color=BAR_BLUE, edgecolor="white", linewidth=0.8, zorder=2)
    ms = base.metric_stats[0]
    if ms.mean   is not None: ax.axvline(ms.mean,   color=MEAN_COL,   linewidth=1.5, label=f"Mean: {ms.mean:.1f}")
    if ms.median is not None: ax.axvline(ms.median, color=MEDIAN_COL, linewidth=1.5, label=f"Median: {ms.median:.1f}")

    peer_colour_idx = 0
    for ps in population_shapes[1:]:
        if ps.role == "Selected":
            sel_vals = [u.values[0] for u in ps.shape.units if u.values[0] is not None]
            if sel_vals and report_context:
                sv = sel_vals[0]
                ax.axvline(sv, color=HIGHLIGHT, linewidth=2, linestyle="--", zorder=4,
                           label=f"{report_context.submission_code}: {sv:g}")
        else:
            colour = PEER_COLOURS[peer_colour_idx % len(PEER_COLOURS)]
            peer_colour_idx += 1
            peer_vals = [u.values[0] for u in ps.shape.units if u.values[0] is not None]
            if peer_vals:
                peer_mean = float(np.mean(peer_vals))
                ax.axvline(peer_mean, color=colour, linewidth=1.5, linestyle="--",
                           label=f"{ps.label} mean: {peer_mean:.1f}")

    ax.set_title(base.title or "", fontsize=10, fontweight="bold", pad=10)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(_k_fmt))
    ax.tick_params(labelsize=8)
    ax.set_ylabel("Count", fontsize=8)
    ax.yaxis.grid(True, color="#E0E0E0", linewidth=0.7)
    _apply_spine_style(ax)
    ax.legend(fontsize=7, frameon=False)
    fig.tight_layout()
    sel_val = next((u.values[0] for ps in population_shapes if ps.role == "Selected"
                    for u in ps.shape.units if u.values[0] is not None), None)
    stats = {
        "Min":            round(ms.min,   1) if ms.min    is not None else None,
        "Lower Quartile": round(ms.q1,    1) if ms.q1     is not None else None,
        "Mean":           round(ms.mean,  1) if ms.mean   is not None else None,
        "Median":         round(ms.median,1) if ms.median is not None else None,
        "Upper Quartile": round(ms.q3,    1) if ms.q3     is not None else None,
        "Max":            round(ms.max,   1) if ms.max    is not None else None,
    }
    return _fig_to_bytes(fig), _autotable_with_selection(stats, report_context, sel_val)


def violin_plot(population_shapes: list, width=50, height=50, tweaks=[], report_context=None):
    """Violin plot — distribution from first shape, markers for subsequent layers."""
    base = population_shapes[0].shape
    w, h = _size_to_inches(width, height)
    fig, ax = plt.subplots(figsize=(w, h))
    values = [u.values[0] for u in base.units if u.values[0] is not None]
    parts = ax.violinplot(values, vert=True, showmedians=True, showextrema=True)
    for pc in parts["bodies"]:
        pc.set_facecolor(BAR_BLUE); pc.set_edgecolor(NAVY); pc.set_alpha(0.75)
    parts["cmedians"].set_color(MEDIAN_COL); parts["cmedians"].set_linewidth(2)
    parts["cmaxes"].set_color(NAVY); parts["cmins"].set_color(NAVY); parts["cbars"].set_color(NAVY)
    ms = base.metric_stats[0]
    if ms.mean is not None:
        ax.scatter([1], [ms.mean], color=MEAN_COL, zorder=5, s=50)

    extra_handles = []
    peer_colour_idx = 0
    for ps in population_shapes[1:]:
        if ps.role == "Selected":
            sel_vals = [u.values[0] for u in ps.shape.units if u.values[0] is not None]
            if sel_vals and report_context:
                sv = sel_vals[0]
                ax.scatter([1], [sv], color=HIGHLIGHT, zorder=7, s=80, marker="D")
                ax.axhline(sv, color=HIGHLIGHT, linewidth=1, linestyle=":", zorder=5, alpha=0.6)
                extra_handles.append(plt.Line2D([0],[0], marker="D", color="w",
                    markerfacecolor=HIGHLIGHT, markersize=7,
                    label=f"{report_context.submission_code}: {sv:g}"))
        else:
            colour = PEER_COLOURS[peer_colour_idx % len(PEER_COLOURS)]
            peer_colour_idx += 1
            if report_context:
                sel_in_peer = next((u.values[0] for u in ps.shape.units
                                    if u.submission_id == report_context.submission_id
                                    and u.values[0] is not None), None)
                if sel_in_peer is not None:
                    ax.scatter([1], [sel_in_peer], color=colour, zorder=6, s=60, marker="D", alpha=0.85)
                    ax.axhline(sel_in_peer, color=colour, linewidth=0.8, linestyle=":", zorder=5, alpha=0.5)
                    extra_handles.append(plt.Line2D([0],[0], marker="D", color="w",
                        markerfacecolor=colour, markersize=6, label=ps.label))

    ax.set_xticks([])
    ax.set_title(base.title or "", fontsize=10, fontweight="bold", pad=10)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(_k_fmt))
    ax.tick_params(axis="y", labelsize=9)
    ax.yaxis.grid(True, color="#E0E0E0", linewidth=0.7)
    _apply_spine_style(ax)
    ax.set_xlabel(f"n = {len(values)}", fontsize=8, color="#555555")
    handles = [
        mpatches.Patch(facecolor=BAR_BLUE, edgecolor=NAVY, alpha=0.75, label="Distribution"),
        plt.Line2D([0],[0], color=MEDIAN_COL, linewidth=2,
                   label=f"Median: {ms.median:.1f}" if ms.median else "Median"),
        plt.Line2D([0],[0], marker="o", color="w", markerfacecolor=MEAN_COL, markersize=6,
                   label=f"Mean: {ms.mean:.1f}" if ms.mean else "Mean"),
    ] + extra_handles
    ax.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, -0.08),
              ncol=3, fontsize=7, frameon=False)
    fig.tight_layout()
    sel_val = next((u.values[0] for ps in population_shapes if ps.role == "Selected"
                    for u in ps.shape.units if u.values[0] is not None), None)
    stats = {
        "Lower Quartile": round(ms.q1,    1) if ms.q1     is not None else None,
        "Mean":           round(ms.mean,  1) if ms.mean   is not None else None,
        "Median":         round(ms.median,1) if ms.median is not None else None,
        "Upper Quartile": round(ms.q3,    1) if ms.q3     is not None else None,
    }
    return _fig_to_bytes(fig), _autotable_with_selection(stats, report_context, sel_val)


# ===========================================================================
# NUMERIC COMPOSITIONAL
# Population layers not applicable — charts render aggregated sample averages.
# ===========================================================================

def ugly_bar(population_shapes: list, width=80, height=40, tweaks=[], report_context=None):
    """Horizontal bar — component breakdown (sample average)."""
    base = population_shapes[0].shape
    w, h = _size_to_inches(width, height)
    fig, ax = plt.subplots(figsize=(w, h))
    metric = base.metrics[0]
    components = metric.component_names
    values = [v if v is not None else 0 for v in metric.units[0].values]
    y = np.arange(len(components))
    ax.barh(y, values, color=BAR_BLUE, height=0.5, zorder=2)
    ax.set_yticks(y)
    ax.set_yticklabels(components, fontsize=8)
    ax.invert_yaxis()
    if base.format_modifier == "P":
        ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:.0f}%"))
        ax.set_xlim(0, max(values) * 1.15 if values else 100)
    ax.set_title(base.title or "", fontsize=10, fontweight="bold", pad=10)
    ax.tick_params(axis="x", labelsize=8)
    ax.xaxis.grid(True, color="#E0E0E0", linewidth=0.7)
    _apply_spine_style(ax)
    handles = [
        mpatches.Patch(color=BAR_BLUE,  label="Sample Average"),
        mpatches.Patch(color="#AAAAAA", label="Submission"),
    ]
    ax.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, -0.15),
              ncol=2, fontsize=7, frameon=False)
    fig.tight_layout()
    return _fig_to_bytes(fig), _autotable_with_selection(
        {c: round(v, 1) for c, v in zip(components, values)}, report_context, None)


def radar_chart(population_shapes: list, width=55, height=55, tweaks=[], report_context=None):
    """Radar / spider chart — component values on radial axes."""
    base = population_shapes[0].shape
    w, h = _size_to_inches(width, height)
    fig = plt.figure(figsize=(w, h))
    metric = base.metrics[0]
    components = metric.component_names
    values = [v if v is not None else 0 for v in metric.units[0].values]
    N = len(components)
    angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
    values_plot = values + [values[0]]
    angles_plot = angles + [angles[0]]
    ax = fig.add_subplot(111, polar=True)
    ax.plot(angles_plot, values_plot, color=NAVY, linewidth=2, zorder=3)
    ax.fill(angles_plot, values_plot, color=BAR_BLUE, alpha=0.35, zorder=2)
    ax.scatter(angles, values, color=NAVY, s=40, zorder=4)
    ax.set_xticks(angles)
    labels = [c if len(c) <= 18 else c[:16] + "…" for c in components]
    ax.set_xticklabels(labels, fontsize=7.5)
    ax.tick_params(axis="y", labelsize=7, colors="#888888")
    ax.yaxis.grid(True, color="#DDDDDD", linewidth=0.7)
    ax.xaxis.grid(True, color="#DDDDDD", linewidth=0.7)
    ax.spines["polar"].set_visible(False)
    if base.format_modifier == "P":
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:.0f}%"))
    ax.set_title(base.title or "", fontsize=10, fontweight="bold", pad=20)
    fig.tight_layout()
    return _fig_to_bytes(fig), _autotable_with_selection(
        {c: round(v, 1) for c, v in zip(components, values)}, report_context, None)


def donut_component(population_shapes: list, width=55, height=55, tweaks=[], report_context=None):
    """Donut chart showing component proportions."""
    base = population_shapes[0].shape
    w, h = _size_to_inches(width, height)
    fig, ax = plt.subplots(figsize=(w, h))
    metric = base.metrics[0]
    components = metric.component_names
    values = [v if v is not None else 0 for v in metric.units[0].values]
    total = sum(values) or 1
    colours = PIE_COLOURS[:len(components)]
    wedges, _, autotexts = ax.pie(
        values, colors=colours, startangle=90,
        autopct=lambda p: f"{p:.1f}%" if p > 5 else "",
        pctdistance=0.75,
        wedgeprops={"width": 0.55, "linewidth": 1.5, "edgecolor": "white"},
    )
    for at in autotexts:
        at.set_fontsize(8); at.set_color("white"); at.set_fontweight("bold")
    ax.set_title(base.title or "", fontsize=10, fontweight="bold", pad=10)
    ax.legend(wedges, [f"{c} ({v/total*100:.1f}%)" for c, v in zip(components, values)],
              loc="upper center", bbox_to_anchor=(0.5, -0.02),
              fontsize=7, frameon=False, ncol=2)
    fig.tight_layout()
    return _fig_to_bytes(fig), _autotable_with_selection(
        {c: round(v/total*100, 1) for c, v in zip(components, values)}, report_context, None)


def lollipop_chart(population_shapes: list, width=70, height=40, tweaks=[], report_context=None):
    """Lollipop chart — stem and dot per component."""
    base = population_shapes[0].shape
    w, h = _size_to_inches(width, height)
    fig, ax = plt.subplots(figsize=(w, h))
    metric = base.metrics[0]
    components = metric.component_names
    values = [v if v is not None else 0 for v in metric.units[0].values]
    y = np.arange(len(components))
    ax.hlines(y, 0, values, color=BAR_BLUE, linewidth=2.5, zorder=2)
    ax.scatter(values, y, color=NAVY, s=80, zorder=3)
    for i, (val, yi) in enumerate(zip(values, y)):
        fmt = f"{val:.1f}%" if base.format_modifier == "P" else f"{val:g}"
        ax.text(val + max(values) * 0.02, yi, fmt, va="center", fontsize=8, color=NAVY)
    ax.set_yticks(y)
    ax.set_yticklabels(components, fontsize=8)
    ax.invert_yaxis()
    ax.set_xlim(0, max(values) * 1.2 if values else 100)
    ax.set_title(base.title or "", fontsize=10, fontweight="bold", pad=10)
    ax.tick_params(axis="x", labelsize=8)
    if base.format_modifier == "P":
        ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:.0f}%"))
    ax.xaxis.grid(True, color="#E0E0E0", linewidth=0.7)
    _apply_spine_style(ax)
    fig.tight_layout()
    return _fig_to_bytes(fig), _autotable_with_selection(
        {c: round(v, 1) for c, v in zip(components, values)}, report_context, None)


def waffle_chart(population_shapes: list, width=60, height=50, tweaks=[], report_context=None):
    """Waffle chart — 10×10 grid, each cell ≈ 1%."""
    base = population_shapes[0].shape
    w, h = _size_to_inches(width, height)
    fig, ax = plt.subplots(figsize=(w, h))
    metric = base.metrics[0]
    components = metric.component_names
    values = [v if v is not None else 0 for v in metric.units[0].values]
    total = sum(values) or 1
    pcts = [v / total * 100 for v in values]
    cells = []
    for i, p in enumerate(pcts):
        cells.extend([i] * round(p))
    cells = cells[:100]
    while len(cells) < 100:
        cells.append(len(components) - 1)
    colours = PIE_COLOURS[:len(components)]
    grid = np.array(cells).reshape(10, 10)
    for row in range(10):
        for col in range(10):
            cat_idx = grid[row, col]
            rect = plt.Rectangle((col, 9 - row), 0.9, 0.9,
                                  facecolor=colours[cat_idx], edgecolor="white", linewidth=1.5)
            ax.add_patch(rect)
    ax.set_xlim(0, 10); ax.set_ylim(0, 10)
    ax.set_aspect("equal"); ax.axis("off")
    ax.set_title(base.title or "", fontsize=10, fontweight="bold", pad=10)
    handles = [mpatches.Patch(color=colours[i], label=f"{components[i]} ({pcts[i]:.1f}%)")
               for i in range(len(components))]
    ax.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, -0.02),
              fontsize=7, frameon=False, ncol=2)
    fig.tight_layout()
    return _fig_to_bytes(fig), _autotable_with_selection(
        {c: round(p, 1) for c, p in zip(components, pcts)}, report_context, None)


# ===========================================================================
# CATEGORICAL COMPOSITIONAL
# Population layers not applicable — charts render population-level aggregates.
# ===========================================================================

def yn_bar(population_shapes: list, width=80, height=55, tweaks=[], report_context=None):
    """Horizontal stacked Yes/No bar per question."""
    base = population_shapes[0].shape
    w, h = _size_to_inches(width, height)
    fig, ax = plt.subplots(figsize=(w, h))
    questions, yes_pcts, no_pcts = [], [], []
    for metric in base.metrics:
        total = metric.stats.count_with_data or 1
        counts = metric.stats.component_counts
        yes_pcts.append((counts[0] / total * 100) if len(counts) > 0 else 0)
        no_pcts.append( (counts[1] / total * 100) if len(counts) > 1 else 0)
        questions.append(metric.name or "")
    y = np.arange(len(questions))
    ax.barh(y, yes_pcts, color=YES_COL, height=0.5, zorder=2)
    ax.barh(y, no_pcts,  color=NO_COL,  height=0.5, left=yes_pcts, zorder=2)
    ax.set_yticks(y); ax.set_yticklabels(questions, fontsize=7)
    ax.invert_yaxis()
    ax.set_xlim(0, 100)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:.0f}%"))
    ax.xaxis.set_major_locator(mticker.MultipleLocator(5))
    ax.xaxis.tick_top(); ax.xaxis.set_label_position("top")
    ax.set_title(base.title or "", fontsize=10, fontweight="bold", pad=20)
    ax.tick_params(axis="x", labelsize=7)
    ax.xaxis.grid(True, color="#E0E0E0", linewidth=0.7)
    ax.spines["bottom"].set_visible(False); ax.spines["right"].set_visible(False)
    ax.set_axisbelow(True)
    handles = [mpatches.Patch(color=YES_COL, label="Yes"), mpatches.Patch(color=NO_COL, label="No")]
    ax.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, -0.03),
              ncol=2, fontsize=7, frameon=False)
    fig.tight_layout()
    return _fig_to_bytes(fig), _autotable_with_selection(
        {q: {"Yes %": round(yp,1), "No %": round(np_,1)}
         for q, yp, np_ in zip(questions, yes_pcts, no_pcts)},
        report_context, None)


def list_pie(population_shapes: list, width=50, height=55, tweaks=[], report_context=None):
    """Pie chart — category proportions for a single metric."""
    base = population_shapes[0].shape
    w, h = _size_to_inches(width, height)
    fig, ax = plt.subplots(figsize=(w, h))
    metric = base.metrics[0]
    categories = metric.category_names
    counts = metric.stats.component_counts
    total = sum(c for c in counts if c is not None)
    if total == 0:
        ax.text(0.5, 0.5, "No data", ha="center", va="center", transform=ax.transAxes)
        return _fig_to_bytes(fig), _autotable_with_selection({}, report_context, None)
    pcts = [c / total * 100 for c in counts]
    colours = PIE_COLOURS[:len(categories)]
    wedges, _, autotexts = ax.pie(pcts, colors=colours, startangle=90,
                                   autopct=lambda p: f"{p:.1f}%" if p > 4 else "",
                                   pctdistance=0.65,
                                   wedgeprops={"linewidth": 1.5, "edgecolor": "white"})
    for at in autotexts:
        at.set_fontsize(8); at.set_color("white"); at.set_fontweight("bold")
    for wedge, cat, pct in zip(wedges, categories, pcts):
        angle = (wedge.theta1 + wedge.theta2) / 2
        rad = np.radians(angle)
        x_i, y_i = 1.05 * np.cos(rad), 1.05 * np.sin(rad)
        x_o, y_o = 1.28 * np.cos(rad), 1.28 * np.sin(rad)
        ax.annotate(f"{cat}: {pct:.1f}%", xy=(x_i, y_i), xytext=(x_o, y_o),
                    fontsize=7.5, ha="left" if x_o > 0 else "right", va="center",
                    arrowprops=dict(arrowstyle="-", color="#888888", lw=0.8))
    ax.set_title(base.title or "", fontsize=10, fontweight="bold", pad=12)
    fig.tight_layout()
    return _fig_to_bytes(fig), _autotable_with_selection(
        {cat: round(pct, 1) for cat, pct in zip(categories, pcts)}, report_context, None)


def diverging_bar(population_shapes: list, width=80, height=55, tweaks=[], report_context=None):
    """Diverging bar — Yes right / No left from centre axis."""
    base = population_shapes[0].shape
    w, h = _size_to_inches(width, height)
    fig, ax = plt.subplots(figsize=(w, h))
    questions, yes_pcts, no_pcts = [], [], []
    for metric in base.metrics:
        total = metric.stats.count_with_data or 1
        counts = metric.stats.component_counts
        yes_pcts.append((counts[0] / total * 100) if len(counts) > 0 else 0)
        no_pcts.append( (counts[1] / total * 100) if len(counts) > 1 else 0)
        questions.append(metric.name or "")
    y = np.arange(len(questions))
    ax.barh(y,  yes_pcts,              color=YES_COL, height=0.55, zorder=2)
    ax.barh(y, [-n for n in no_pcts],  color=NO_COL,  height=0.55, zorder=2)
    ax.axvline(0, color="#333333", linewidth=0.8, zorder=3)
    ax.set_yticks(y); ax.set_yticklabels(questions, fontsize=7)
    ax.invert_yaxis()
    lim = max(max(yes_pcts), max(no_pcts)) * 1.1
    ax.set_xlim(-lim, lim)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{abs(v):.0f}%"))
    ax.set_title(base.title or "", fontsize=10, fontweight="bold", pad=10)
    ax.tick_params(axis="x", labelsize=7)
    ax.xaxis.grid(True, color="#E0E0E0", linewidth=0.7)
    _apply_spine_style(ax)
    ax.text( lim * 0.5,  -0.8, "Yes →", ha="center", va="center", fontsize=8, color=YES_COL, fontweight="bold")
    ax.text(-lim * 0.5,  -0.8, "← No",  ha="center", va="center", fontsize=8, color=NO_COL,  fontweight="bold")
    fig.tight_layout()
    return _fig_to_bytes(fig), _autotable_with_selection(
        {q: {"Yes %": round(yp,1), "No %": round(np_,1)}
         for q, yp, np_ in zip(questions, yes_pcts, no_pcts)},
        report_context, None)


def dot_matrix(population_shapes: list, width=80, height=55, tweaks=[], report_context=None):
    """Dot matrix — filled dots per category per question, each dot ≈ 10%."""
    base = population_shapes[0].shape
    w, h = _size_to_inches(width, height)
    is_yn = (len(base.metrics) > 1 and
             base.metrics[0].category_names == ["Yes", "No"])
    if is_yn:
        metrics = base.metrics
        categories = ["Yes", "No"]
        counts_list = [m.stats.component_counts for m in metrics]
        totals = [m.stats.count_with_data or 1 for m in metrics]
        questions = [m.name or "" for m in metrics]
    else:
        metric = base.metrics[0]
        categories = metric.category_names
        counts_list = [metric.stats.component_counts]
        totals = [metric.stats.count_with_data or 1]
        questions = [metric.name or ""]

    n_q = len(questions)
    n_c = len(categories)
    fig, ax = plt.subplots(figsize=(w, h))
    colours_use = [YES_COL, NO_COL] if is_yn else PIE_COLOURS[:n_c]

    for qi, (q, counts, total) in enumerate(zip(questions, counts_list, totals)):
        pcts = [(c / total * 100) if c else 0 for c in counts]
        for ci, (cat, pct, col) in enumerate(zip(categories, pcts, colours_use)):
            n_filled = round(pct / 10)
            for d in range(10):
                filled = d < n_filled
                ax.scatter(ci * 11 + d, qi,
                           s=55, color=col if filled else "#E0E0E0",
                           zorder=2, linewidths=0)

    ax.set_yticks(range(n_q)); ax.set_yticklabels(questions, fontsize=7)
    ax.invert_yaxis()
    ax.set_xticks([ci * 11 + 4.5 for ci in range(n_c)])
    ax.set_xticklabels(categories, fontsize=8, fontweight="bold")
    ax.tick_params(bottom=False)
    ax.set_title(base.title or "", fontsize=10, fontweight="bold", pad=10)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.yaxis.grid(False); ax.set_facecolor("white")
    ax.text(0, n_q + 0.3, "Each dot ≈ 10%", fontsize=6.5, color="#888888", style="italic")
    fig.tight_layout()
    return _fig_to_bytes(fig), _autotable_with_selection({}, report_context, None)


def donut_pie(population_shapes: list, width=50, height=55, tweaks=[], report_context=None):
    """Donut ring chart."""
    base = population_shapes[0].shape
    w, h = _size_to_inches(width, height)
    fig, ax = plt.subplots(figsize=(w, h))
    metric = base.metrics[0]
    categories = metric.category_names
    counts = metric.stats.component_counts
    total = sum(c for c in counts if c is not None)
    if total == 0:
        ax.text(0.5, 0.5, "No data", ha="center", va="center", transform=ax.transAxes)
        return _fig_to_bytes(fig), _autotable_with_selection({}, report_context, None)
    pcts = [c / total * 100 for c in counts]
    colours = PIE_COLOURS[:len(categories)]
    wedges, _ = ax.pie(pcts, colors=colours, startangle=90,
                        wedgeprops={"width": 0.5, "linewidth": 2, "edgecolor": "white"})
    for wedge, cat, pct in zip(wedges, categories, pcts):
        angle = (wedge.theta1 + wedge.theta2) / 2
        rad = np.radians(angle)
        x_o, y_o = 1.22 * np.cos(rad), 1.22 * np.sin(rad)
        ax.annotate(f"{cat}\n{pct:.1f}%", xy=(0.88*np.cos(rad), 0.88*np.sin(rad)),
                    xytext=(x_o, y_o), fontsize=7.5,
                    ha="left" if x_o > 0 else "right", va="center",
                    arrowprops=dict(arrowstyle="-", color="#AAAAAA", lw=0.6))
    ax.set_title(base.title or "", fontsize=10, fontweight="bold", pad=12)
    fig.tight_layout()
    return _fig_to_bytes(fig), _autotable_with_selection(
        {cat: round(pct, 1) for cat, pct in zip(categories, pcts)}, report_context, None)


def treemap(population_shapes: list, width=65, height=45, tweaks=[], report_context=None):
    """Treemap — area-proportional category rectangles."""
    base = population_shapes[0].shape
    w, h = _size_to_inches(width, height)
    fig, ax = plt.subplots(figsize=(w, h))
    metric = base.metrics[0]
    categories = metric.category_names
    counts = metric.stats.component_counts
    total = sum(c for c in counts if c is not None) or 1
    pcts = [c / total * 100 for c in counts]
    colours = PIE_COLOURS[:len(categories)]
    sorted_items = sorted(zip(pcts, categories, colours), reverse=True)
    x_cursor = 0
    for pct, cat, col in sorted_items:
        bw = pct / 100
        rect = plt.Rectangle((x_cursor, 0), bw, 1.0,
                              facecolor=col, edgecolor="white", linewidth=2)
        ax.add_patch(rect)
        cx, cy = x_cursor + bw / 2, 0.5
        if bw > 0.06:
            ax.text(cx, cy + 0.15, cat, ha="center", va="center",
                    fontsize=8, color="white", fontweight="bold")
            ax.text(cx, cy - 0.15, f"{pct:.1f}%", ha="center", va="center",
                    fontsize=8, color="white")
        x_cursor += bw
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    ax.set_title(base.title or "", fontsize=10, fontweight="bold", pad=10)
    fig.tight_layout()
    return _fig_to_bytes(fig), _autotable_with_selection(
        {cat: round(pct, 1) for cat, pct in zip(categories, pcts)}, report_context, None)


# ===========================================================================
# BEAD STRING DOT PLOT — NumericSeries, tier-per-population-shape
# ===========================================================================

def bead_string_dot_plot(population_shapes: list, width=80, height=40, tweaks=[], report_context=None):
    """Multi-tier bead-string dot plot — one tier per population shape."""
    if not population_shapes:
        fig, ax = plt.subplots()
        ax.text(0.5, 0.5, "No data", ha="center", va="center")
        return _fig_to_bytes(fig), {}

    base = population_shapes[0].shape
    ms   = base.metric_stats[0] if base.metric_stats else None
    vals = [u.values[0] for u in base.units if u.values[0] is not None]
    if not vals:
        fig, ax = plt.subplots()
        ax.text(0.5, 0.5, "No data", ha="center", va="center")
        return _fig_to_bytes(fig), {}

    COLOUR_ALL = (136/255, 135/255, 128/255, 0.38)
    STRING_ALL = (136/255, 135/255, 128/255, 0.25)
    COLOUR_SEL = "#185FA5"
    STRING_SEL = (24/255, 95/255, 165/255, 0.20)

    tiers = []
    peer_colour_idx = 0
    for ps in population_shapes:
        tier_vals = [u.values[0] for u in ps.shape.units if u.values[0] is not None]
        if not tier_vals:
            continue
        if ps.role == "All":
            tiers.append({"vals": tier_vals, "dot": COLOUR_ALL, "string": STRING_ALL,
                          "label": "All organisations", "opaque": False})
        elif ps.role == "Selected":
            tiers.append({"vals": tier_vals, "dot": COLOUR_SEL, "string": STRING_SEL,
                          "label": ps.label or "Selected", "opaque": True})
        else:
            raw = PEER_COLOURS[peer_colour_idx % len(PEER_COLOURS)]
            r, g, b = mcolors.to_rgb(raw)
            tiers.append({"vals": tier_vals, "dot": (r, g, b, 0.42), "string": (r, g, b, 0.20),
                          "label": ps.label, "opaque": False})
            peer_colour_idx += 1

    if not tiers:
        fig, ax = plt.subplots()
        ax.text(0.5, 0.5, "No data", ha="center", va="center")
        return _fig_to_bytes(fig), {}

    n_tiers = len(tiers)
    w, _   = _size_to_inches(width, height)
    TIER_GAP = 0.40; LABEL_COL = 1.6; DOT_SIZE = 38
    INCHES_PER_TIER = 0.28; MARGIN_TOP = 0.40; MARGIN_BOT = 0.25
    h = n_tiers * INCHES_PER_TIER + MARGIN_TOP + MARGIN_BOT

    for i, t in enumerate(tiers):
        t["y"] = i * TIER_GAP

    y_min = -TIER_GAP
    y_max = (n_tiers - 1) * TIER_GAP + TIER_GAP

    all_vals_flat = [v for t in tiers for v in t["vals"]]
    x_min = min(all_vals_flat); x_max = max(all_vals_flat)
    pad = (x_max - x_min) * 0.05 or 1.0
    x_min -= pad; x_max += pad

    if ms:
        q1, q3, median = ms.q1, ms.q3, ms.median
    else:
        q1 = float(np.percentile(vals, 25))
        q3 = float(np.percentile(vals, 75))
        median = float(np.median(vals))

    fig = plt.figure(figsize=(w, h))
    left_frac   = LABEL_COL / w
    bottom_frac = MARGIN_BOT / h
    height_frac = (h - MARGIN_TOP - MARGIN_BOT) / h
    ax = fig.add_axes([left_frac, bottom_frac, 1 - left_frac - 0.02, height_frac])

    ax.set_xlim(x_min, x_max); ax.set_ylim(y_min, y_max); ax.set_yticks([])
    ax.spines["left"].set_visible(False); ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False); ax.spines["bottom"].set_visible(True)
    ax.spines["bottom"].set_color("#CCCCCC")
    ax.tick_params(axis="x", labelsize=7.5, color="#AAAAAA"); ax.xaxis.grid(False)

    if q1 is not None and q3 is not None:
        iqr_rect = mpatches.FancyBboxPatch(
            (q1, y_min), q3 - q1, y_max - y_min,
            boxstyle="square,pad=0",
            facecolor=(181/255, 212/255, 244/255, 0.38), edgecolor="none", zorder=1)
        ax.add_patch(iqr_rect)
        label_y = y_max + TIER_GAP * 0.08
        ax.text(q1, label_y, f"Q1\n{q1:.1f}", ha="center", va="bottom",
                fontsize=6.5, color=(100/255, 130/255, 180/255, 0.85))
        ax.text(q3, label_y, f"Q3\n{q3:.1f}", ha="center", va="bottom",
                fontsize=6.5, color=(100/255, 130/255, 180/255, 0.85))

    if median is not None:
        ax.vlines(median, y_min, y_max, colors="#E24B4A", linewidth=1.2, linestyles="dashed", zorder=3)
        ax.text(median, y_max + TIER_GAP * 0.08, f"Median\n{median:.1f}",
                ha="center", va="bottom", fontsize=6.5, color="#E24B4A")

    for t in tiers:
        y = t["y"]; dot = t["dot"]; str_c = t["string"]
        ax.hlines(y, x_min, x_max, colors=[str_c], linewidths=0.5, zorder=2)
        alpha = 1.0 if t["opaque"] else (dot[3] if len(dot) == 4 else 1.0)
        dot_c = dot[:3] if isinstance(dot, tuple) else dot
        ax.scatter(t["vals"], [y] * len(t["vals"]),
                   s=DOT_SIZE, c=[dot_c] * len(t["vals"]),
                   alpha=alpha, linewidths=0, zorder=4)

    if tiers[-1]["opaque"] and tiers[-1]["vals"]:
        sv = tiers[-1]["vals"][0]
        ax.annotate(f"{sv:.1f}", xy=(sv, tiers[-1]["y"]),
                    xytext=(0, 9), textcoords="offset points",
                    ha="center", fontsize=7.5, color=COLOUR_SEL, fontweight="bold")

    ax_pos = ax.get_position()
    for t in tiers:
        y_ax  = (t["y"] - y_min) / (y_max - y_min)
        y_fig = ax_pos.y0 + y_ax * ax_pos.height
        dot_c = t["dot"][:3] if isinstance(t["dot"], tuple) else t["dot"]
        fig.text(ax_pos.x0 - 0.045, y_fig, t["label"],
                 ha="right", va="center", fontsize=7.5, color="#444444")
        r_y = 0.014; r_x = r_y * (h / w)
        fig.patches.append(mpatches.Ellipse(
            (ax_pos.x0 - 0.030, y_fig), width=2*r_x, height=2*r_y,
            transform=fig.transFigure, facecolor=dot_c, edgecolor="none", alpha=0.75, zorder=5))

    title = base.title or (base.metric_names[0] if base.metric_names else "")
    if title:
        fig.text(ax_pos.x0, ax_pos.y0 + ax_pos.height + 0.10,
                 title, ha="left", va="bottom", fontsize=9, fontweight="bold",
                 color="#222222", transform=fig.transFigure)

    sel_val = tiers[-1]["vals"][0] if tiers[-1]["opaque"] and tiers[-1]["vals"] else None
    stats = {
        "Lower Quartile": round(q1,     1) if q1     is not None else None,
        "Median":         round(median, 1) if median is not None else None,
        "Upper Quartile": round(q3,     1) if q3     is not None else None,
    }
    return _fig_to_bytes(fig), _autotable_with_selection(stats, report_context, sel_val)


# ===========================================================================
# Registry + dispatch
# ===========================================================================

CHART_REGISTRY = {
    "ranked_column":        ranked_column,
    "dot_strip":            dot_strip,
    "box_whisker":          box_whisker,
    "frequency_histogram":  frequency_histogram,
    "violin_plot":          violin_plot,
    "ugly_bar":             ugly_bar,
    "radar_chart":          radar_chart,
    "donut_component":      donut_component,
    "lollipop_chart":       lollipop_chart,
    "waffle_chart":         waffle_chart,
    "yn_bar":               yn_bar,
    "list_pie":             list_pie,
    "diverging_bar":        diverging_bar,
    "dot_matrix":           dot_matrix,
    "donut_pie":            donut_pie,
    "treemap":              treemap,
    "bead_string_dot_plot": bead_string_dot_plot,
}


def render_chart(chart_type_ref: str, population_shapes: list,
                 width: int, height: int, tweaks=[], report_context=None):
    if chart_type_ref not in CHART_REGISTRY:
        raise ValueError(f"Unknown chart_type_ref: {chart_type_ref}")
    return CHART_REGISTRY[chart_type_ref](
        population_shapes, width=width, height=height,
        tweaks=tweaks, report_context=report_context,
    )
