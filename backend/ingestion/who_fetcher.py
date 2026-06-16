import httpx
from typing import List, Dict

WHO_ENDPOINTS = {
    "cholera": "https://ghoapi.azureedge.net/api/CHOLERA_0000000001?$top=100",
    "malaria": "https://ghoapi.azureedge.net/api/MALARIA_EST_DEATHS?$top=100",
}

def fetch_who_data() -> List[Dict]:
    records = []
    with httpx.Client(timeout=30) as client:
        for disease, url in WHO_ENDPOINTS.items():
            try:
                response = client.get(url)
                response.raise_for_status()
                data = response.json().get("value", [])
                for item in data:
                    item["_disease"] = disease
                    item["_source"] = "WHO"
                records.extend(data)
                print(f"WHO {disease}: fetched {len(data)} records")
            except Exception as e:
                print(f"WHO {disease} fetch failed: {e}")
    return records