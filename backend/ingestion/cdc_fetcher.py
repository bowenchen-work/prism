import httpx
from typing import List, Dict

CDC_ENDPOINTS = {
    "flu": "https://data.cdc.gov/resource/ph8t-4gbt.json?$limit=100",
    "covid": "https://data.cdc.gov/resource/pwn4-m3yp.json?$limit=100",
}

def fetch_cdc_data() -> List[Dict]:
    records = []
    with httpx.Client(timeout=30) as client:
        for disease, url in CDC_ENDPOINTS.items():
            try:
                response = client.get(url)
                response.raise_for_status()
                data = response.json()
                for item in data:
                    item["_disease"] = disease
                    item["_source"] = "CDC"
                records.extend(data)
                print(f"CDC {disease}: fetched {len(data)} records")
            except Exception as e:
                print(f"CDC {disease} fetch failed: {e}")
    return records