import requests
from typing import List, Dict, Any

def extract_from_url(url: str, limit: int = 50, auth_header: str = "") -> List[Dict[str, Any]]:
    """
    Dynamically fetches records from any user-supplied REST API URL.
    Handles:
    - Arrays directly returned by the API ([{...}, {...}])
    - Wrapped object responses ({"products": [...]}, {"data": [...]}, {"results": [...]}, {"items": [...]})
    - Dynamic query parameters for pagination where supported
    """
    headers = {
        "User-Agent": "Automated-ETL-Pipeline/1.0",
        "Accept": "application/json"
    }
    if auth_header.strip():
        headers["Authorization"] = auth_header.strip()

    all_records: List[Dict[str, Any]] = []

    try:
        # First attempt: check if endpoint responds directly
        response = requests.get(url, headers=headers, timeout=12)
        response.raise_for_status()
        payload = response.json()

        # Parse structure
        extracted_list = []
        if isinstance(payload, list):
            extracted_list = payload
        elif isinstance(payload, dict):
            # Check common API payload keys
            for key in ["products", "data", "results", "items", "records", "coins", "posts", "entries"]:
                if key in payload and isinstance(payload[key], list):
                    extracted_list = payload[key]
                    break
            
            # If still not found, search for any list value inside dictionary
            if not extracted_list:
                for v in payload.values():
                    if isinstance(v, list) and len(v) > 0 and isinstance(v[0], dict):
                        extracted_list = v
                        break

        # If it has standard pagination (like DummyJSON), pull additional pages if possible
        if isinstance(payload, dict) and "total" in payload and "skip" in payload:
            total = payload.get("total", len(extracted_list))
            all_records.extend(extracted_list)
            skip = len(extracted_list)
            
            while skip < total and skip < 250: # Safe upper bound for dynamic fetches
                separator = "&" if "?" in url else "?"
                paged_url = f"{url}{separator}skip={skip}&limit={limit}"
                resp = requests.get(paged_url, headers=headers, timeout=12)
                resp.raise_for_status()
                pdata = resp.json()
                items = pdata.get("products") or pdata.get("data") or []
                if not items:
                    break
                all_records.extend(items)
                skip += len(items)
        else:
            all_records.extend(extracted_list)

    except requests.exceptions.RequestException as exc:
        raise RuntimeError(f"API request failed: {exc}") from exc

    return all_records
