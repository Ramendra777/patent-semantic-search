import pandas as pd
import requests
import json
import time
import os
import random
from datetime import datetime
from sentence_transformers import SentenceTransformer
from pymilvus import connections, utility, FieldSchema, CollectionSchema, DataType, Collection

# Use 'milvus-standalone' as default for Docker environment
MILVUS_HOST = os.getenv("MILVUS_HOST", "milvus-standalone")
MILVUS_PORT = os.getenv("MILVUS_PORT", "19530")
COLLECTION_NAME = "documents"
MODEL_NAME = 'all-MiniLM-L6-v2'
BATCH_SIZE = 100
TARGET_PATENTS = 50
TARGET_PAPERS = 50

def reconstruct_openalex_abstract(inverted_index):
    if not inverted_index:
        return ""
    try:
        max_pos = max([pos for positions in inverted_index.values() for pos in positions])
        words = [""] * (max_pos + 1)
        for word, positions in inverted_index.items():
            for pos in positions:
                words[pos] = word
        return " ".join(words).strip()
    except:
        return ""

def fetch_openalex(query="machine learning", target_count=50):
    """Fetch research papers from OpenAlex with a local mock fallback."""
    print(f"Fetching OpenAlex papers for query: {query}")
    url = f"https://api.openalex.org/works?filter=abstract.search:%22{query}%22&per_page=200"
    papers = []
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', [])
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
    except Exception as e:
        print(f"OpenAlex Fetch Error: {e}")
    
    if len(papers) < target_count:
        needed = target_count - len(papers)
        print(f"Generating {needed} mock research papers...")
        for i in range(needed):
            papers.append({
                'doc_id': f"mock_paper_{i}_{random.randint(1000,9999)}",
                'title': f"Deep Dive into {query.title()} - Study {i}",
                'abstract': f"This paper presents a formal analysis of {query} and its applications in automated systems. " * 10,
                'doc_type': 'Research Paper',
                'publication_date': f"2023-{random.randint(1,12):02d}-{random.randint(1,28):02d}",
                'citation_count': random.randint(5, 150)
            })
            
    return pd.DataFrame(papers)

def parse_patents(file_path, limit=TARGET_PATENTS):
    print(f"Attempting to parse patents from: {file_path}")
    patents = []
    
    if os.path.exists(file_path):
        try:
            df_iter = pd.read_csv(file_path, sep='\t', chunksize=1000, on_bad_lines='skip', engine='python')
            for chunk in df_iter:
                chunk = chunk.dropna(subset=['patent_abstract'])
                for _, row in chunk.iterrows():
                    abstract = str(row['patent_abstract']).strip()
                    if len(abstract) < 50: continue
                    
                    pid = str(row['patent_id'])
                    pub_date = f"{random.randint(2010, 2024)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}"
                    
                    patents.append({
                        "doc_id": f"patent_{pid}",
                        "title": f"Patent Publication US-{pid}-A1",
                        "abstract": abstract,
                        "doc_type": "Patent",
                        "publication_date": pub_date,
                        "citation_count": random.randint(1, 40)
                    })
                    if len(patents) >= limit: break
                if len(patents) >= limit: break
        except Exception as e:
            print(f"Error reading patent file: {e}")
            
    if len(patents) < limit:
        needed = limit - len(patents)
        print(f"Generating {needed} mock patents...")
        topics = ["machine learning", "neural networks", "autonomous vehicles", "quantum computing", "biotechnology"]
        for i in range(needed):
            topic = random.choice(topics)
            patents.append({
                "doc_id": f"patent_mock_{i}",
                "title": f"System and Method for {topic.title()} Optimization",
                "abstract": f"A patented invention describing a novel approach to {topic} using specialized circuitry and algorithmic processing. Facilitates improved efficiency in data-heavy environments. " * 8,
                "doc_type": "Patent",
                "publication_date": f"2024-{random.randint(1,3):02d}-{random.randint(1,28):02d}",
                "citation_count": random.randint(0, 15)
            })
            
    return pd.DataFrame(patents)

def init_milvus():
    print(f"Connecting to Milvus at {MILVUS_HOST}:{MILVUS_PORT}...")
    # Add retry logic for connection in docker
    for attempt in range(5):
        try:
            connections.connect("default", host=MILVUS_HOST, port=MILVUS_PORT, timeout=10)
            print("Connected successfully.")
            break
        except Exception as e:
            print(f"Connection attempt {attempt+1} failed: {e}. Retrying in 5s...")
            time.sleep(5)
    else:
        raise Exception("Could not connect to Milvus after 5 attempts.")
    
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
    collection.create_index(field_name="doc_type")
    collection.create_index(field_name="publication_date")
    collection.create_index(field_name="citation_count")
    
    collection.load()
    return collection

def ingest_data():
    # Try various relative paths for the patent file
    paths_to_try = [
        'g_patent_abstract.tsv/g_patent_abstract.tsv',
        '../g_patent_abstract.tsv/g_patent_abstract.tsv',
        './g_patent_abstract.tsv/g_patent_abstract.tsv'
    ]
    patents_df = pd.DataFrame()
    for p in paths_to_try:
        patents_df = parse_patents(p)
        if not patents_df.empty: break
        
    papers_df = fetch_openalex()
    df = pd.concat([patents_df, papers_df], ignore_index=True)
    
    print(f"Total documents prepared for ingestion: {len(df)}")
    collection = init_milvus()
    
    print("Loading embedding model...")
    model = SentenceTransformer(MODEL_NAME)
    
    for i in range(0, len(df), BATCH_SIZE):
        batch = df.iloc[i:i+BATCH_SIZE]
        
        doc_ids = [str(x)[:190] for x in batch['doc_id'].tolist()]
        titles = [str(x)[:490] for x in batch['title'].tolist()]
        abstracts = [str(x)[:14000] for x in batch['abstract'].tolist()]
        doc_types = [str(x)[:45] for x in batch['doc_type'].tolist()]
        dates = [str(x)[:19] for x in batch['publication_date'].tolist()]
        citations = [int(x) if pd.notnull(x) else 0 for x in batch['citation_count'].tolist()]
        
        print(f"Encoding batch {i}...")
        embeddings = model.encode(abstracts, normalize_embeddings=True).tolist()
        
        entities = [doc_ids, titles, abstracts, doc_types, dates, citations, embeddings]
        collection.insert(entities)
        print(f"Inserted {len(batch)} entities.")
    
    collection.flush()
    print(f"Ingestion complete. Total entities in Milvus: {collection.num_entities}")

if __name__ == "__main__":
    ingest_data()
