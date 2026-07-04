"""
cache_reader.py
Loads a canonical data shape from the data cache by filename.
Deserialises the JSON back into the appropriate dataclass instance.

Works against ProjectState.cache when available, or falls back to
reading from m11_data_cache/ on disk.
"""

import json
import os

from modules.m04_data_shapes.shapes import (
    NumericSeries, NumericSeriesUnit, NumericSeriesMetricStats, ShapeStats,
    NumericCompositional, NumericCompositionalMetric, NumericCompositionalUnit,
    NumericCompositionalMetricStats,
    CategoricalCompositional, CategoricalCompositionalMetric,
    CategoricalCompositionalUnit, CategoricalCompositionalMetricStats,
)

CACHE_DIR = os.path.join(os.path.dirname(__file__), "..", "m11_data_cache")


def _from_dict_numeric_series(d):
    units = [
        NumericSeriesUnit(
            submission_code=u["submission_code"],
            submission_id=u["submission_id"],
            values=u["values"],
        )
        for u in d.get("units", [])
    ]
    metric_stats = [
        NumericSeriesMetricStats(**ms)
        for ms in d.get("metric_stats", [])
    ]
    return NumericSeries(
        title=d.get("title"),
        metric_names=d.get("metric_names", []),
        year=d.get("year"),
        format_modifier=d.get("format_modifier"),
        has_valid_unit_data=d.get("has_valid_unit_data", True),
        units=units,
        shape_stats=ShapeStats(**d.get("shape_stats", {})),
        metric_stats=metric_stats,
    )


def _from_dict_numeric_compositional(d):
    metrics = []
    for m in d.get("metrics", []):
        units = [
            NumericCompositionalUnit(
                submission_code=u["submission_code"],
                submission_id=u["submission_id"],
                values=u["values"],
            )
            for u in m.get("units", [])
        ]
        metrics.append(NumericCompositionalMetric(
            name=m.get("name"),
            component_names=m.get("component_names", []),
            units=units,
            stats=NumericCompositionalMetricStats(**m.get("stats", {})),
        ))
    return NumericCompositional(
        title=d.get("title"),
        year=d.get("year"),
        format_modifier=d.get("format_modifier"),
        has_valid_unit_data=d.get("has_valid_unit_data", True),
        metrics=metrics,
        shape_stats=ShapeStats(**d.get("shape_stats", {})),
    )


def _from_dict_categorical_compositional(d):
    metrics = []
    for m in d.get("metrics", []):
        units = [
            CategoricalCompositionalUnit(
                submission_code=u["submission_code"],
                submission_id=u["submission_id"],
                response=u.get("response"),
            )
            for u in m.get("units", [])
        ]
        metrics.append(CategoricalCompositionalMetric(
            name=m.get("name"),
            category_names=m.get("category_names", []),
            units=units,
            stats=CategoricalCompositionalMetricStats(**m.get("stats", {})),
        ))
    return CategoricalCompositional(
        title=d.get("title"),
        year=d.get("year"),
        has_valid_unit_data=d.get("has_valid_unit_data", True),
        metrics=metrics,
        shape_stats=ShapeStats(**d.get("shape_stats", {})),
    )


DESERIALISE_MAP = {
    "NumericSeries":            _from_dict_numeric_series,
    "NumericCompositional":     _from_dict_numeric_compositional,
    "CategoricalCompositional": _from_dict_categorical_compositional,
}


def _deserialise(json_str: str):
    wrapper = json.loads(json_str)
    shape_type = wrapper["shape_type"]
    data = wrapper["data"]
    if shape_type not in DESERIALISE_MAP:
        raise ValueError(f"Unknown shape_type in cache: {shape_type}")
    return DESERIALISE_MAP[shape_type](data), shape_type


def load_shape(filename, project_state=None):
    """
    Load a cached data shape by filename (e.g. '88141_0_0.json').
    Uses ProjectState.cache if provided, otherwise reads from disk.
    Returns (shape_instance, shape_type_string).
    """
    if project_state is not None and filename in project_state.cache:
        return _deserialise(project_state.cache[filename])

    path = os.path.join(CACHE_DIR, filename)
    with open(path, "r", encoding="utf-8") as f:
        return _deserialise(f.read())


def list_cached_files(project_state=None):
    """Return sorted list of cache filenames (excluding manifest)."""
    if project_state is not None:
        return sorted(project_state.cache.keys())

    files = [
        f for f in os.listdir(CACHE_DIR)
        if f.endswith(".json") and f != "manifest.json"
    ]
    return sorted(files)


def load_manifest(project_state=None):
    """
    Return manifest dict keyed by filename.
    Uses ProjectState.manifest if provided, otherwise reads from disk.
    """
    if project_state is not None:
        return {v["filename"]: v for v in project_state.manifest.values()}

    path = os.path.join(CACHE_DIR, "manifest.json")
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        entries = json.load(f)
    return {v["filename"]: v for v in entries.values()}
