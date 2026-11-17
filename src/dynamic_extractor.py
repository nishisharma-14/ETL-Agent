import requests
from typing import List, Dict, Any

def extract_from_url(url: str, limit: int = 50, auth_header: str = "") -> List[Dict[str, Any]]:
    """
    Dynamically fetches records from any user-supplied REST API URL.
    Handles:
    - Stripping documentation fragment hashes (#/...)
    - Detecting HTML responses (Swagger / web pages) and providing friendly errors
    - Passing API Keys either as Bearer tokens or custom header tokens (e.g. X-API-Key)
    - Parsing arrays or wrapped object responses
    """
    clean_url = url.strip()

    # If user accidentally pastes a Swagger UI URL like https://.../docs#/Tickets/...
    # Warn and point them to the raw endpoint
    if "/docs#" in clean_url or "/docs" in clean_url.split("?")[0].rstrip("/").split("/")[-1:]:
        raise ValueError(
            "You entered a Swagger Documentation webpage URL instead of the actual API data endpoint. "
            "Please use the actual data endpoint path (e.g., https://reinventapi.awslpu.in/api/v1/tickets/categories) "
            "instead of /docs#/... and supply your API key in the auth field."
        )

    headers = {
        "User-Agent": "Automated-ETL-Pipeline/1.0",
        "Accept": "application/json"
    }

    token = auth_header.strip()
    if token:
        # Check if user passed full header or raw token
        if token.lower().startswith("bearer ") or token.lower().startswith("apikey "):
            headers["Authorization"] = token
            headers["X-API-Key"] = token.split(" ", 1)[-1]
        else:
            headers["Authorization"] = f"Bearer {token}"
            headers["X-API-Key"] = token

    all_records: List[Dict[str, Any]] = []

    try:
        response = requests.get(clean_url, headers=headers, timeout=12)
        
        # Check content-type to catch HTML pages early
        content_type = response.headers.get("content-type", "").lower()
        if "text/html" in content_type:
            raise ValueError(
                f"The target URL returned an HTML webpage (status {response.status_code}) instead of JSON data. "
                "Ensure you are calling the raw API JSON endpoint."
            )

        # Catch 401 Unauthorized with helpful message
        if response.status_code == 401:
            raise ValueError(
                "API returned 401 Unauthorized: Invalid or missing API key. "
                "Please provide your API key in the 'Optional Bearer Token / API Key' input field."
            )
        elif response.status_code == 403:
            raise ValueError(
                "API returned 403 Forbidden: You do not have permission to access this endpoint."
            )

        response.raise_for_status()

        try:
            payload = response.json()
        except Exception as json_err:
            raise ValueError(
                f"Failed to parse JSON from response. Received non-JSON body: {response.text[:200]}"
            ) from json_err

        # Parse data structure
        extracted_list = []
        if isinstance(payload, list):
            extracted_list = payload
        elif isinstance(payload, dict):
            # Check common API payload keys
            for key in ["data", "categories", "tickets", "products", "results", "items", "records", "coins"]:
                if key in payload and isinstance(payload[key], list):
                    extracted_list = payload[key]
                    break
            
            # If not found, look for any list inside the dict
            if not extracted_list:
                for v in payload.values():
                    if isinstance(v, list) and len(v) > 0 and isinstance(v[0], dict):
                        extracted_list = v
                        break
                # If still single object or dict with items
                if not extracted_list and "success" in payload and isinstance(payload.get("data"), dict):
                    extracted_list = [payload["data"]]

        # Handle pagination if total & skip exist
        if isinstance(payload, dict) and "total" in payload and "skip" in payload:
            total = payload.get("total", len(extracted_list))
            all_records.extend(extracted_list)
            skip = len(extracted_list)
            
            while skip < total and skip < 250:
                separator = "&" if "?" in clean_url else "?"
                paged_url = f"{clean_url}{separator}skip={skip}&limit={limit}"
                resp = requests.get(paged_url, headers=headers, timeout=12)
                resp.raise_for_status()
                pdata = resp.json()
                items = pdata.get("products") or pdata.get("data") or pdata.get("categories") or []
                if not items:
                    break
                all_records.extend(items)
                skip += len(items)
        else:
            all_records.extend(extracted_list)

    except requests.exceptions.RequestException as exc:
        raise RuntimeError(f"Network request failed: {exc}") from exc

    return all_records
