"""
cache_writer.py
Serialises canonical data shapes and saves them to the data cache.
Maintains the manifest with metadata and fetch timestamps.

Works against ProjectState when available, or falls back to disk
(m11_data_cache/) for backwards compatibility.

File naming: {tier_id}_{group}_{option}.json
"""

import json
import os
import dataclasses
from datetime import datetime, timezone


CACHE_DIR = os.path.join(os.path.dirname(__file__), "..", "m11_data_cache")
MANIFEST_PATH = os.path.join(CACHE_DIR, "manifest.json")


def _serialise(obj):
    """Recursively serialise dataclasses to dicts for JSON output."""
    if dataclasses.is_dataclass(obj) and not isinstance(obj, type):
        return {k: _serialise(v) for k, v in dataclasses.asdict(obj).items()}
    if isinstance(obj, list):
        return [_serialise(v) for v in obj]
    return obj


def save_chart(tier_id: int, group: int, option: int, label: str, shape, shape_type: str,
               url: str = "", project_state=None) -> str:
    """
    Serialise a canonical data shape and save to the cache.

    If project_state is provided, writes into ProjectState.cache and
    ProjectState.manifest in memory (marks state dirty).
    Otherwise falls back to writing to m11_data_cache/ on disk.

    Returns a nominal filepath string (used for logging).
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

    if project_state is not None:
        project_state.cache[filename] = json_str
        project_state.manifest[key] = manifest_entry
        project_state.dirty = True
        return filename
    else:
        os.makedirs(CACHE_DIR, exist_ok=True)
        filepath = os.path.join(CACHE_DIR, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(json_str)
        _update_manifest_disk(key, manifest_entry)
        return filepath


def _update_manifest_disk(key: str, entry: dict):
    manifest = _load_manifest_disk()
    manifest[key] = entry
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)


def _load_manifest_disk() -> dict:
    if os.path.exists(MANIFEST_PATH):
        with open(MANIFEST_PATH, encoding="utf-8") as f:
            return json.load(f)
    return {}


def load_manifest() -> dict:
    return _load_manifest_disk()
