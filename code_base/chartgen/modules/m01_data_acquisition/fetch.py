"""
fetch.py
Orchestrates the full data acquisition process.

For each URL in urls.csv:
  1. Parse the URL into components
  2. API call 1: get tier info (reportId, year, serviceItemId)
  3. API call 2: get chart data (raw JSON)
  4. Transform raw JSON into a canonical data shape
  5. Save normalised shape to m11_data_cache

Called once before a batch run. Not called during batch processing.
"""

import os
from .url_parser import load_urls, parse_url
from .api_client import get_tier_info, get_chart_data
from .transformers import transform
from .cache_writer import save_chart

PROJECT_CONFIG_DIR = os.path.join(os.path.dirname(__file__), "..", "m10_project_config")
URLS_PATH = os.path.join(PROJECT_CONFIG_DIR, "urls.csv")


def fetch_all(token: str, on_progress=None, project_state=None) -> list[dict]:
    """
    Fetch, transform, and cache data for all URLs in the project config.

    token: session token from st.session_state, obtained at login.
    on_progress: optional callback(current, total, label) for UI progress updates.

    Returns a list of result dicts, one per URL:
    {
        "tier_id": int,
        "label": str,
        "status": "ok" | "error",
        "message": str,
        "filepath": str | None,
        "shape_type": str | None,
    }
    """
    if project_state is not None:
        urls = [parse_url(u["url"], u.get("label", "")) for u in project_state.urls if u.get("url")]
    else:
        urls = load_urls(URLS_PATH)
    results = []
    total = len(urls)

    for i, parsed in enumerate(urls):
        tier_id = parsed["tier_id"]
        group   = parsed["group"]
        option  = parsed["option"]
        label   = parsed["label"]

        if on_progress:
            on_progress(i + 1, total, label)

        try:
            # API call 1: tier metadata
            tier_info  = get_tier_info(tier_id, token)
            data_block = tier_info["data"]
            # Use most recent visible year
            report_years = data_block["reportYears"]
            visible = [y for y in report_years if y.get("isVisible") == "Y"]
            latest = max(visible or report_years, key=lambda y: y["reportYear"])
            report_id      = str(latest["reportId"])
            year           = str(latest["reportYear"])
            service_item_id = str(data_block.get("serviceItemId") or "0")

            # API call 2: chart data
            raw_json = get_chart_data(
                report_id=report_id,
                group=group,
                year=year,
                service_item_id=service_item_id,
                option=option,
                token=token,
            )

            # Transform to canonical shape
            shape = transform(raw_json, year)
            shape_type = type(shape).__name__

            # Save normalised shape to cache
            filepath = save_chart(tier_id, group, option, label, shape, shape_type, url=parsed["url"], project_state=project_state)

            results.append({
                "tier_id":    tier_id,
                "label":      label,
                "status":     "ok",
                "message":    f"{shape_type} → {os.path.basename(filepath)}",
                "filepath":   filepath,
                "shape_type": shape_type,
            })

        except Exception as e:
            results.append({
                "tier_id":    tier_id,
                "label":      label,
                "status":     "error",
                "message":    str(e),
                "filepath":   None,
                "shape_type": None,
            })

    return results
