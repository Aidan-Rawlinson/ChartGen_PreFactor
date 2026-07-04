"""
url_parser.py
Parses toolkit URLs into their component parts.
Each URL yields: project_id, tier_id, group, option, and label.
"""

from urllib.parse import urlparse, parse_qs
import csv


def parse_url(url: str, label: str = "") -> dict:
    """
    Parse a single toolkit URL into its components.

    Example URL:
    https://members.nhsbenchmarking.nhs.uk/outputs/6?tier=88141&group=0

    Returns:
    {
        "url": original URL,
        "label": human-readable label from CSV,
        "project_id": 6,
        "tier_id": 88141,
        "group": 0,
        "option": 0
    }
    """
    parsed = urlparse(url)

    # project_id is the final segment of the path e.g. /outputs/6 -> 6
    path_parts = parsed.path.rstrip("/").split("/")
    project_id = int(path_parts[-1])

    # Query parameters
    params = parse_qs(parsed.query)
    tier_id = int(params.get("tier", [0])[0])
    group = int(params.get("group", [0])[0])
    option = int(params.get("option", [0])[0])

    return {
        "url": url,
        "label": label.strip(),
        "project_id": project_id,
        "tier_id": tier_id,
        "group": group,
        "option": option,
    }


def load_urls(csv_path: str) -> list[dict]:
    """
    Load and parse all URLs from the project config CSV.
    CSV format: url,label (no header row).
    Returns a list of parsed URL dicts.
    """
    results = []
    with open(csv_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        for row in reader:
            if not row or not row[0].strip():
                continue
            url = row[0].strip()
            label = row[1].strip() if len(row) > 1 else ""
            results.append(parse_url(url, label))
    return results
