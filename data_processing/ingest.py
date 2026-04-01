import pandas as pd
import requests
import json
import time
import os
import random
from datetime import datetime
from sentence_transformers import SentenceTransformer
from pymilvus import connections, utility, FieldSchema, CollectionSchema, DataType, Collection

MILVUS_URI = os.getenv("MILVUS_URI") # Zilliz Cloud URI
MILVUS_TOKEN = os.getenv("MILVUS_TOKEN") # Zilliz Cloud API Key
COLLECTION_NAME = "documents"
MODEL_NAME = 'all-MiniLM-L6-v2'
BATCH_SIZE = 100
TARGET_PATENTS = 50
TARGET_PAPERS = 50

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

def fetch_openalex(query="machine learning", target_count=500):
    """Fetch research papers from OpenAlex with a local mock fallback."""
    print(f"Fetching OpenAlex papers for query: {query}")
    url = f"https://api.openalex.org/works?filter=abstract.search:%22{query}%22&per_page=200"
    papers = []
    page = 1
    
    try:
        while len(papers) < target_count:
            # Add a timeout to the request to avoid hanging
            response = requests.get(f"{url}&page={page}", timeout=10)
            if response.status_code != 200:
                print(f"OpenAlex API error {response.status_code}. Using mock fallback.")
                break
            data = response.json()
            results = data.get('results', [])
            if not results:
                break
            
            for work in results:
                abstract = reconstruct_openalex_abstract(work.get('abstract_inverted_index'))
                if abstract and len(abstract) > 50:
                    papers.append({
                        'doc_id': str(work.get('id')),
                        'title': str(work.get('display_name', 'Research Paper')),
                        'abstract': abstract,
                        'doc_type': 'Research Paper',
                        'publication_date': str(work.get('publication_date', '2023-01-01')),
                        'citation_count': int(work.get('cited_by_count', 0))
                    })
                if len(papers) >= target_count:
                    break
            page += 1
            print(f"Fetched {len(papers)} papers...")
    except Exception as e:
        print(f"OpenAlex Fetch Error: {e}. Switching to mock data generation.")
    
    # Mock data fallback if API fails or returns insufficient results
    if len(papers) < target_count:
        needed = target_count - len(papers)
        print(f"Generating {needed} mock research papers...")
        for i in range(needed):
            papers.append({
                'doc_id': f"https://openalex.org/MOCK{i}",
                'title': f"Advances in {query.title()} Research - Vol {i}",
                'abstract': f"This simulated research paper explores the implications of {query} in modern engineering. " * 15,
                'doc_type': 'Research Paper',
                'publication_date': f"2023-{random.randint(1,12):02d}-{random.randint(1,28):02d}",
                'citation_count': random.randint(0, 100)
            })
            
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
    if MILVUS_URI and MILVUS_TOKEN:
        connections.connect("default", uri=MILVUS_URI, token=MILVUS_TOKEN)
    else:
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
        "metric_type": "L2",
        "index_type": "IVF_FLAT",
        "params": {"nlist": 128}
    }
    collection.create_index(field_name="embedding", index_params=index_params)
    
    # Create indexes for scalar fields (optional but recommended for filtering)
    collection.create_index(field_name="doc_type")
    collection.create_index(field_name="publication_date")
    collection.create_index(field_name="citation_count")
    
    collection.load()
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
    
    # Clean and truncate data
    for i in range(0, len(df), BATCH_SIZE):
        batch = df.iloc[i:i+BATCH_SIZE]

        
        # Clean and truncate data
        doc_ids = [str(x)[:190] for x in batch['doc_id'].tolist()]
        titles = [str(x)[:490] for x in batch['title'].tolist()]
        abstracts = [str(x)[:14000] for x in batch['abstract'].tolist()] # Safe truncation
        doc_types = [str(x)[:45] for x in batch['doc_type'].tolist()]
        dates = [str(x)[:19] for x in batch['publication_date'].tolist()]
        citations = [int(x) if pd.notnull(x) else 0 for x in batch['citation_count'].tolist()]
        
        print(f"Encoding batch {i} to {i+len(batch)}...")
        embeddings = model.encode(abstracts, normalize_embeddings=True).tolist()
        
        entities = [
            doc_ids,
            titles,
            abstracts,
            doc_types,
            dates,
            citations,
            embeddings
        ]
        
        res = collection.insert(entities)
        print(f"Inserted {res.insert_count} entities.")
    
    collection.flush()

    print(f"Insertion complete. Total entities in Milvus: {collection.num_entities}")

if __name__ == "__main__":
    ingest_data()
