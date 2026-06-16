from ingestion.cdc_fetcher import fetch_cdc_data
from ingestion.who_fetcher import fetch_who_data
from ingestion.chunker import chunk_records
from ingestion.embedder import embed_and_store

def main():
    print("=== Starting Prism ingestion ===")
    
    print("\n[1/4] Fetching CDC data...")
    cdc_records = fetch_cdc_data()
    
    print("\n[2/4] Fetching WHO data...")
    who_records = fetch_who_data()
    
    all_records = cdc_records + who_records
    print(f"\n[3/4] Chunking {len(all_records)} records...")
    chunks = chunk_records(all_records)
    print(f"Generated {len(chunks)} chunks")
    
    print("\n[4/4] Embedding and storing...")
    stored = embed_and_store(chunks)
    print(f"\n=== Done. {stored} new chunks stored in pgvector ===")

if __name__ == "__main__":
    main()