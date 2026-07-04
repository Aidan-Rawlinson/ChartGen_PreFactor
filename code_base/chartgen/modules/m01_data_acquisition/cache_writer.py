"""
cache_writer.py
Serialises canonical data shapes and saves them to the data cache.
Maintains the manifest with metadata and fetch timestamps.

Works against WorkfileState — the sole live store for cached chart data.

File naming: {tier_id}_{group}_{option}.json
"""

import json
import dataclasses
from datetime import datetime, timezone


def _serialise(obj):
    """Recursively serialise dataclasses to dicts for JSON output."""
    if dataclasses.is_dataclass(obj) and not isinstance(obj, type):
        return {k: _serialise(v) for k, v in dataclasses.asdict(obj).items()}
    if isinstance(obj, list):
        return [_serialise(v) for v in obj]
    return obj


def save_chart(tier_id: int, group: int, option: int, label: str, shape, shape_type: str,
               url: str = "", *, workfile_state) -> str:
    """
    Serialise a canonical data shape and save it into WorkfileState.cache and
    WorkfileState.manifest in memory (marks state dirty).

    Returns the cache filename (used for logging).
    """
    filename = f"{tier_id}_{group}_{option}.json"
    payload = {
        "shape_type": shape_type,
        "data": _serialise(shape),
    }
    json_str = json.dumps(payload, indent=2)

    key = f"{tier_id}_{group}_{option}"
    manifest_entry = {
        "tier_id":      tier_id,
        "group":        group,
        "option":       option,
        "label":        label,
        "filename":     filename,
        "shape_type":   shape_type,
        "url":          url,
        "last_fetched": datetime.now(timezone.utc).isoformat(),
    }

    workfile_state.cache[filename] = json_str
    workfile_state.manifest[key] = manifest_entry
    workfile_state.dirty = True
    return filename
