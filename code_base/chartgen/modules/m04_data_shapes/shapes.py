"""
shapes.py
Canonical data shapes for ChartGen — NumericSeries, NumericCompositional, and CategoricalCompositional.
"""

from dataclasses import dataclass, field
from typing import Optional


# ---------------------------------------------------------------------------
# Shared: comparative unit entry base
# ---------------------------------------------------------------------------

@dataclass
class ComparativeUnit:
    """Identity fields shared by all per-unit entries across all shapes."""
    submission_code: str
    submission_id:   int


# ---------------------------------------------------------------------------
# Shape-level stats (shared structure, same meaning across all shapes)
# ---------------------------------------------------------------------------

@dataclass
class ShapeStats:
    """Shape-level summary statistics, identical in structure across all three shapes."""
    count_metric_series:        Optional[int] = None  # number of Metric-Series in this shape
    count_comparative_units:    Optional[int] = None  # total units in population
    count_units_with_any_data:  Optional[int] = None  # units with data in at least one Metric-Series


# ---------------------------------------------------------------------------
# NumericSeries
# ---------------------------------------------------------------------------

@dataclass
class NumericSeriesMetricStats:
    """Metric-Series-level stats for a NumericSeries shape."""
    count_with_data:    Optional[int]   = None
    count_null:         Optional[int]   = None
    mean:               Optional[float] = None
    median:             Optional[float] = None
    q1:                 Optional[float] = None
    q3:                 Optional[float] = None
    min:                Optional[float] = None
    max:                Optional[float] = None


@dataclass
class NumericSeriesUnit(ComparativeUnit):
    """One comparative unit's values across one or more independent Metric-Series."""
    values: list[Optional[float]] = field(default_factory=list)


@dataclass
class NumericSeries:
    """One or more independent numeric Metric-Series across a comparative population."""
    # Metadata
    title:              Optional[str]       = None
    metric_names:       list[str]           = field(default_factory=list)  # one per Metric-Series
    year:               Optional[int]       = None
    format_modifier:    Optional[str]       = None

    # Data
    has_valid_unit_data: bool               = True
    units:              list[NumericSeriesUnit] = field(default_factory=list)

    # Stats — shape level, then one Metric-Series stats block per series
    shape_stats:        ShapeStats          = field(default_factory=ShapeStats)
    metric_stats:       list[NumericSeriesMetricStats] = field(default_factory=list)


# ---------------------------------------------------------------------------
# NumericCompositional
# ---------------------------------------------------------------------------

@dataclass
class NumericCompositionalMetricStats:
    """Metric-Series-level stats for a NumericCompositional shape."""
    count_with_data:        Optional[int]           = None  # units with at least one non-null component
    count_null:             Optional[int]            = None  # units with all components null
    component_counts_with_data: list[Optional[int]] = field(default_factory=list)  # one per Component-Series


@dataclass
class NumericCompositionalUnit(ComparativeUnit):
    """One comparative unit's values for one Metric-Series in a NumericCompositional shape."""
    values: list[Optional[float]] = field(default_factory=list)


@dataclass
class NumericCompositionalMetric:
    """One Metric-Series within a NumericCompositional shape."""
    name:               Optional[str]                       = None
    component_names:    list[str]                           = field(default_factory=list)
    units:              list[NumericCompositionalUnit]      = field(default_factory=list)
    stats:              NumericCompositionalMetricStats     = field(default_factory=NumericCompositionalMetricStats)


@dataclass
class NumericCompositional:
    """One or more Metric-Series per comparative unit, each composed of Component-Series summing to a whole."""
    # Metadata
    title:              Optional[str]       = None
    year:               Optional[int]       = None
    format_modifier:    Optional[str]       = None

    # Data — one NumericCompositionalMetric per Metric-Series
    has_valid_unit_data: bool               = True
    metrics:            list[NumericCompositionalMetric] = field(default_factory=list)

    # Shape-level stats
    shape_stats:        ShapeStats          = field(default_factory=ShapeStats)


@dataclass
class CategoricalCompositionalMetricStats:
    """Metric-Series-level stats for a CategoricalCompositional shape."""
    count_with_data:            Optional[int]           = None  # units that gave a response
    count_null:                 Optional[int]            = None  # units with no response
    component_counts:           list[Optional[int]]     = field(default_factory=list)  # one count per category


@dataclass
class CategoricalCompositionalUnit(ComparativeUnit):
    """One comparative unit's response for one Metric-Series (question)."""
    response: Optional[str] = None


@dataclass
class CategoricalCompositionalMetric:
    """One Metric-Series (question) within a CategoricalCompositional shape."""
    name:               Optional[str]                           = None
    category_names:     list[str]                               = field(default_factory=list)
    units:              list[CategoricalCompositionalUnit]      = field(default_factory=list)
    stats:              CategoricalCompositionalMetricStats     = field(default_factory=CategoricalCompositionalMetricStats)


@dataclass
class CategoricalCompositional:
    """One or more Metric-Series (questions) per comparative population, each with categorical Component-Series that sum to a whole."""
    # Metadata
    title:              Optional[str]       = None
    year:               Optional[int]       = None

    # Data — one CategoricalCompositionalMetric per question/Metric-Series
    has_valid_unit_data: bool               = True
    metrics:            list[CategoricalCompositionalMetric] = field(default_factory=list)

    # Shape-level stats
    shape_stats:        ShapeStats          = field(default_factory=ShapeStats)
# ---------------------------------------------------------------------------
# Population shape container
# ---------------------------------------------------------------------------

@dataclass
class PopulationShape:
    """A filtered data shape representing one population layer."""
    role:  str
    label: str
    shape: object  # NumericSeries | NumericCompositional | CategoricalCompositional


# ---------------------------------------------------------------------------
# Stats recalculation helpers
# ---------------------------------------------------------------------------

def _recalc_numeric_series_stats(units: list) -> list:
    """Recalculate NumericSeriesMetricStats for a filtered unit list."""
    if not units:
        return []
    n_metrics = len(units[0].values) if units else 0
    stats = []
    for m in range(n_metrics):
        vals = [u.values[m] for u in units if u.values[m] is not None]
        n_with = len(vals)
        n_null = len(units) - n_with
        if vals:
            arr = sorted(vals)
            n = len(arr)
            mean   = sum(arr) / n
            median = arr[n // 2] if n % 2 else (arr[n//2 - 1] + arr[n//2]) / 2
            q1     = arr[n // 4]
            q3     = arr[3 * n // 4]
            mn, mx = arr[0], arr[-1]
        else:
            mean = median = q1 = q3 = mn = mx = None
        stats.append(NumericSeriesMetricStats(
            count_with_data=n_with, count_null=n_null,
            mean=mean, median=median, q1=q1, q3=q3, min=mn, max=mx,
        ))
    return stats


def _recalc_numeric_compositional_metric_stats(units: list) -> "NumericCompositionalMetricStats":
    n_with = sum(1 for u in units if any(v is not None for v in u.values))
    n_null = len(units) - n_with
    n_comp = len(units[0].values) if units else 0
    comp_counts = []
    for c in range(n_comp):
        comp_counts.append(sum(1 for u in units if c < len(u.values) and u.values[c] is not None))
    return NumericCompositionalMetricStats(
        count_with_data=n_with, count_null=n_null,
        component_counts_with_data=comp_counts,
    )


def _recalc_categorical_metric_stats(units: list, category_names: list) -> "CategoricalCompositionalMetricStats":
    responses = [u.response for u in units]
    n_with = sum(1 for r in responses if r is not None)
    n_null = len(responses) - n_with
    counts = [sum(1 for r in responses if r == cat) for cat in category_names]
    return CategoricalCompositionalMetricStats(
        count_with_data=n_with, count_null=n_null, component_counts=counts,
    )


def filter_numeric_series(shape: "NumericSeries", submission_ids: set) -> "NumericSeries":
    """Return a new NumericSeries filtered to submission_ids with stats recalculated."""
    from dataclasses import replace
    filtered_units = [u for u in shape.units if u.submission_id in submission_ids]
    new_stats = _recalc_numeric_series_stats(filtered_units)
    new_shape_stats = ShapeStats(
        count_metric_series=len(shape.metric_names),
        count_comparative_units=len(filtered_units),
        count_units_with_any_data=sum(1 for u in filtered_units if any(v is not None for v in u.values)),
    )
    return replace(shape, units=filtered_units, metric_stats=new_stats, shape_stats=new_shape_stats)


def filter_numeric_compositional(shape: "NumericCompositional", submission_ids: set) -> "NumericCompositional":
    """Return a new NumericCompositional filtered to submission_ids with stats recalculated."""
    from dataclasses import replace
    new_metrics = []
    for metric in shape.metrics:
        filtered_units = [u for u in metric.units if u.submission_id in submission_ids]
        new_stats = _recalc_numeric_compositional_metric_stats(filtered_units)
        new_metrics.append(replace(metric, units=filtered_units, stats=new_stats))
    n_units = len(new_metrics[0].units) if new_metrics else 0
    new_shape_stats = ShapeStats(
        count_metric_series=len(new_metrics),
        count_comparative_units=n_units,
        count_units_with_any_data=n_units,
    )
    return replace(shape, metrics=new_metrics, shape_stats=new_shape_stats)


def filter_categorical_compositional(shape: "CategoricalCompositional", submission_ids: set) -> "CategoricalCompositional":
    """Return a new CategoricalCompositional filtered to submission_ids with stats recalculated."""
    from dataclasses import replace
    new_metrics = []
    for metric in shape.metrics:
        filtered_units = [u for u in metric.units if u.submission_id in submission_ids]
        new_stats = _recalc_categorical_metric_stats(filtered_units, metric.category_names)
        new_metrics.append(replace(metric, units=filtered_units, stats=new_stats))
    n_units = len(new_metrics[0].units) if new_metrics else 0
    new_shape_stats = ShapeStats(
        count_metric_series=len(new_metrics),
        count_comparative_units=n_units,
        count_units_with_any_data=new_metrics[0].stats.count_with_data if new_metrics else 0,
    )
    return replace(shape, metrics=new_metrics, shape_stats=new_shape_stats)


def filter_shape(shape, submission_ids: set):
    """Dispatch to the correct filter function based on shape type."""
    if isinstance(shape, NumericSeries):
        return filter_numeric_series(shape, submission_ids)
    elif isinstance(shape, NumericCompositional):
        return filter_numeric_compositional(shape, submission_ids)
    elif isinstance(shape, CategoricalCompositional):
        return filter_categorical_compositional(shape, submission_ids)
    raise TypeError(f"Unknown shape type: {type(shape)}")
