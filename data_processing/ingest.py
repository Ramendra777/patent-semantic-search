import pandas as pd
import requests
import json
import time
import os
import random
from datetime import datetime
from sentence_transformers import SentenceTransformer
from pymilvus import connections, utility, FieldSchema, CollectionSchema, DataType, Collection

MILVUS_HOST = os.getenv("MILVUS_HOST", "localhost")
MILVUS_PORT = os.getenv("MILVUS_PORT", "19530")
COLLECTION_NAME = "documents"
MODEL_NAME = 'all-MiniLM-L6-v2'
BATCH_SIZE = 500
TARGET_PATENTS = 30000
TARGET_PAPERS = 30000

def reconstruct_openalex_abstract(inverted_index):
    if not inverted_index:
        return ""
    # inverted_index format: {"word": [positions...], ...}
    max_pos = max([pos for positions in inverted_index.values() for pos in positions])
    words = [""] * (max_pos + 1)
    for word, positions in inverted_index.items():
        for pos in positions:
            words[pos] = word
    return " ".join(words).strip()

def fetch_openalex(limit=TARGET_PAPERS):
    print("Fetching OpenAlex papers...")
    papers = []
    cursor = "*"
    while len(papers) < limit:
        url = f"https://api.openalex.org/works?filter=has_abstract:true&per-page=200&cursor={cursor}"
        resp = requests.get(url)
        if resp.status_code != 200:
            print("Error fetching OpenAlex:", resp.status_code)
            time.sleep(2)
            continue
        
        data = resp.json()
        results = data.get("results", [])
        if not results:
            break
            
        for work in results:
            abstract_idx = work.get("abstract_inverted_index")
            if not abstract_idx:
                continue
            abstract = reconstruct_openalex_abstract(abstract_idx)
            if len(abstract) < 50:
                continue
            title = work.get("title", "Unknown Title")
            if not title:
                title = "Unknown Title"
            pub_date = work.get("publication_date", "2020-01-01")
            if not pub_date:
                pub_date = "2020-01-01"
            citations = work.get("cited_by_count", 0)
            
            papers.append({
                "doc_id": work.get("id"),
                "title": title[:200], # truncate if too long
                "abstract": abstract,
                "doc_type": "Research Paper",
                "publication_date": pub_date,
                "citation_count": citations
            })
            if len(papers) >= limit:
                break
                
        cursor = data.get("meta", {}).get("next_cursor")
        if not cursor:
            break
        print(f"Fetched {len(papers)} papers...")
        
    return pd.DataFrame(papers)

def parse_patents(file_path, limit=TARGET_PATENTS):
    print("Parsing patents...")
    if not os.path.exists(file_path):
        print(f"Patent file not found: {file_path}")
        return pd.DataFrame()
        
    df_iter = pd.read_csv(file_path, sep='\t', chunksize=10000, on_bad_lines='skip', engine='python')
    patents = []
    for chunk in df_iter:
        chunk = chunk.dropna(subset=['patent_abstract'])
        for _, row in chunk.iterrows():
            abstract = str(row['patent_abstract']).strip()
            if len(abstract) < 50:
                continue
            # Mock title and date since they aren't in the provided subset summary
            pid = str(row['patent_id'])
            # Generate a random date between 2000 and 2023 for visualization purposes
            year = random.randint(2000, 2023)
            month = random.randint(1, 12)
            day = random.randint(1, 28)
            pub_date = f"{year}-{month:02d}-{day:02d}"
            
            patents.append({
                "doc_id": f"patent_{pid}",
                "title": f"Patent Authorization {pid}",
                "abstract": abstract,
                "doc_type": "Patent",
                "publication_date": pub_date,
                "citation_count": random.randint(0, 50) # Mock citation
            })
            if len(patents) >= limit:
                break
        if len(patents) >= limit:
            break
            
    return pd.DataFrame(patents)

def init_milvus():
    print("Connecting to Milvus...")
    connections.connect("default", host=MILVUS_HOST, port=MILVUS_PORT)
    
    if utility.has_collection(COLLECTION_NAME):
        print(f"Collection {COLLECTION_NAME} exists. Dropping it to start fresh.")
        utility.drop_collection(COLLECTION_NAME)
        
    fields = [
        FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
        FieldSchema(name="doc_id", dtype=DataType.VARCHAR, max_length=200),
        FieldSchema(name="title", dtype=DataType.VARCHAR, max_length=500),
        FieldSchema(name="abstract", dtype=DataType.VARCHAR, max_length=15000),
        FieldSchema(name="doc_type", dtype=DataType.VARCHAR, max_length=50),
        FieldSchema(name="publication_date", dtype=DataType.VARCHAR, max_length=20),
        FieldSchema(name="citation_count", dtype=DataType.INT64),
        FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=384)
    ]
    schema = CollectionSchema(fields, "Document collection for patents and papers")
    collection = Collection(COLLECTION_NAME, schema)
    
    index_params = {
        "metric_type": "COSINE",
        "index_type": "IVF_FLAT",
        "params": {"nlist": 1024}
    }
    collection.create_index(field_name="embedding", index_params=index_params)
    print("Collection created and indexed.")
    return collection

def ingest_data():
    patents_df = parse_patents('../g_patent_abstract.tsv/g_patent_abstract.tsv')
    papers_df = fetch_openalex()
    
    df = pd.concat([patents_df, papers_df], ignore_index=True)
    if df.empty:
        print("No data collected.")
        return
        
    print(f"Total documents to ingest: {len(df)}")
    
    collection = init_milvus()
    model = SentenceTransformer(MODEL_NAME)
    
    for i in range(0, len(df), BATCH_SIZE):
        batch = df.iloc[i:i+BATCH_SIZE]
        abstracts = batch['abstract'].tolist()
        
        print(f"Encoding batch {i} to {i+len(batch)}...")
        embeddings = model.encode(abstracts, normalize_embeddings=True).tolist()
        
        entities = [
            batch['doc_id'].tolist(),
            batch['title'].tolist(),
            batch['abstract'].tolist(),
            batch['doc_type'].tolist(),
            batch['publication_date'].tolist(),
            batch['citation_count'].tolist(),
            embeddings
        ]
        
        collection.insert(entities)
        
    collection.flush()
    print(f"Insertion complete. Total entities in Milvus: {collection.num_entities}")

if __name__ == "__main__":
    ingest_data()
