import json
from typing import List, Dict

CHUNK_SIZE = 400

def chunk_records(records: List[Dict]) -> List[Dict]:
    chunks = []
    for record in records:
        text = json.dumps(record, default=str)
        words = text.split()
        for i in range(0, len(words), CHUNK_SIZE):
            chunk_words = words[i:i + CHUNK_SIZE]
            chunk_text = " ".join(chunk_words)
            chunks.append({
                "source": record.get("_source", "UNKNOWN"),
                "disease": record.get("_disease", "unknown"),
                "region": record.get("CountryName") or record.get("jurisdiction_residence", "unknown"),
                "date_range": record.get("TimeDim") or record.get("mmwr_year", "unknown"),
                "raw_text": chunk_text,
                "metadata": {"original_keys": list(record.keys())}
            })
    return chunks