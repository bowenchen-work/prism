import os
import psycopg2
import json
from openai import OpenAI
from typing import List, Dict

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_db_connection():
    return psycopg2.connect(os.getenv("DATABASE_URL"))

def embed_and_store(chunks: List[Dict]) -> int:
    conn = get_db_connection()
    cur = conn.cursor()
    stored = 0

    for chunk in chunks:
        cur.execute(
            "SELECT id FROM data_chunks WHERE raw_text = %s",
            (chunk["raw_text"],)
        )
        if cur.fetchone():
            continue

        cur.execute(
            """INSERT INTO data_chunks (source, disease, region, date_range, raw_text, metadata)
               VALUES (%s, %s, %s, %s, %s, %s) RETURNING id""",
            (chunk["source"], chunk["disease"], chunk["region"],
             str(chunk["date_range"]), chunk["raw_text"], json.dumps(chunk["metadata"]))
        )
        chunk_id = cur.fetchone()[0]

        response = client.embeddings.create(
            input=chunk["raw_text"],
            model="text-embedding-3-small"
        )
        vector = response.data[0].embedding

        cur.execute(
            "INSERT INTO embeddings (chunk_id, vector) VALUES (%s, %s)",
            (chunk_id, vector)
        )
        stored += 1

    conn.commit()
    cur.close()
    conn.close()
    return stored