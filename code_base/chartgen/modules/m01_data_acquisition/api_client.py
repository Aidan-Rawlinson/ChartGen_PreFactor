"""
api_client.py
Handles authentication and all API calls to the NHS Benchmarking members API.

Two calls are made per URL:
  1. get_tier_info(tier_id)      -> reportId, reportYear, serviceItemId, serviceItemName
  2. get_chart_data(...)         -> full chart JSON including storedProcedure and data
"""

import requests


BASE_URL = "https://membersapi.nhsbenchmarking.nhs.uk"
ORGANISATION_ID = 232  # Default org used to retrieve full population data


def get_token(username: str, password: str) -> str:
    """
    Authenticate against the API.
    Returns a session token string; raises on invalid credentials or network error.
    """
    response = requests.get(
        f"{BASE_URL}/authentication",
        auth=(username, password),
        headers={"Accept": "application/json"},
    )
    response.raise_for_status()
    return response.json()["data"]["token"]


def get_tier_info(tier_id: int, token: str) -> dict:
    """
    API call 1: retrieve report metadata for a given tier.
    Endpoint: GET /outputs/tiers/{tier_id}/years
    Returns the full parsed JSON response.
    """
    response = requests.get(
        f"{BASE_URL}/outputs/tiers/{tier_id}/years",
        headers={"Accept": "application/json", "Token": token},
    )
    response.raise_for_status()
    return response.json()


def get_projects(year: int, token: str) -> list:
    """
    Retrieve the list of visible projects for a given year.
    Endpoint: GET /projects/list?year={year}
    Returns a list of dicts with keys: project_id, project_name.
    """
    response = requests.get(
        f"{BASE_URL}/projects/list",
        params={"year": year},
        headers={"Accept": "application/json", "Token": token},
    )
    response.raise_for_status()
    project_list = response.json()["data"]["projectList"]
    return [
        {"project_id": p["projectId"], "project_name": p["projectName"]}
        for p in project_list
        if p.get("isVisible", {}).get("description") == "Yes"
    ]


def get_submissions(project_id: int, year: int, token: str, include_org_level: bool = False) -> list:
    """
    Retrieve the submission list for a given project and year.
    Endpoint: GET /submissions/submissionServiceList?projectId={project_id}&year={year}
    Returns a list of dicts, one per submission. Service lists are kept as Python lists.
    Organisational-level submissions (submissionLevel == "O") are excluded by default.
    """
    response = requests.get(
        f"{BASE_URL}/submissions/submissionServiceList",
        params={"projectId": project_id, "year": year},
        headers={"Accept": "application/json", "Token": token},
    )
    response.raise_for_status()
    submission_list = response.json()["data"]["submissionList"][str(year)]

    rows = []
    for s in submission_list:
        if not include_org_level and s.get("submissionLevel") == "O":
            continue

        service_count = s.get("submissionServiceCount", 0) or 0
        services = []
        if service_count > 0 and "serviceList" in s:
            for svc in s["serviceList"]:
                services.append({
                    "service_item_id": svc.get("serviceItemId", ""),
                    "service_item_name": svc.get("serviceItemName", ""),
                    "response_count": svc.get("responseCount", ""),
                })

        rows.append({
            "submission_id": s.get("submissionId", ""),
            "submission_code": s.get("submissionCode", ""),
            "submission_name": s.get("submissionName", ""),
            "submission_year": s.get("submissionYear", ""),
            "project_id": s.get("projectId", ""),
            "project_name": s.get("projectName", ""),
            "organisation_id": s.get("organisationId", ""),
            "organisation_name": s.get("organisationName", ""),
            "submission_service_count": service_count,
            "response_count": s.get("responseCount", ""),
            "submission_level": s.get("submissionLevel", ""),
            "services": services,
        })

    return rows


VALID_ORG_TYPE_IDS = {2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 15, 16, 17, 21, 26}


def get_organisations(year: int, token: str) -> list:
    """
    Retrieve the organisation reference list for a given year.
    Endpoint: GET /organisations?year={year}
    Filters to VALID_ORG_TYPE_IDS. Returns a list of dicts with keys:
    organisation_id, organisation_name, nhs_code, organisation_type_name, region_name.
    """
    response = requests.get(
        f"{BASE_URL}/organisations",
        params={"year": year},
        headers={"Accept": "application/json", "Token": token},
    )
    response.raise_for_status()
    org_list = response.json()["data"]["organisationList"]

    rows = []
    for org in org_list:
        if org.get("organisationTypeId") not in VALID_ORG_TYPE_IDS:
            continue
        rows.append({
            "organisation_id":        org.get("organisationId", ""),
            "organisation_name":      org.get("organisationName", "") or "",
            "nhs_code":               org.get("nhsCode", "") or "",
            "organisation_type_name": org.get("organisationTypeName", "") or "",
            "region_name":            org.get("regionName", "") or "",
        })
    return rows


def get_chart_data(
    report_id: str,
    group: int,
    year: str,
    service_item_id: str,
    option: int,
    token: str,
    organisation_id: int = ORGANISATION_ID,
) -> dict:
    """
    API call 2: retrieve chart data for a given report.
    Endpoint: GET /outputs/{report_id}/data
    Returns the full parsed JSON response.
    """
    if service_item_id == "null" or service_item_id is None:
        service_item_id = "0"

    params = {
        "organisationId": organisation_id,
        "peerGroup": group,
        "year": year,
        "serviceItemId": service_item_id,
        "denominatorOptionId": option,
    }

    response = requests.get(
        f"{BASE_URL}/outputs/{report_id}/data",
        headers={"Accept": "application/json", "Token": token},
        params=params,
    )
    response.raise_for_status()
    return response.json()
