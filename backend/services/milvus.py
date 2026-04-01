import os
from typing import Optional
from pymilvus import connections, Collection

MILVUS_URI = os.getenv("MILVUS_URI") # For Zilliz Cloud
MILVUS_TOKEN = os.getenv("MILVUS_TOKEN") # For Zilliz Cloud
COLLECTION_NAME = "documents"

# Global connection
if MILVUS_URI and MILVUS_TOKEN:
    # Connect to Zilliz Cloud
    connections.connect("default", uri=MILVUS_URI, token=MILVUS_TOKEN)
else:
    # Connect to local Milvus
    connections.connect("default", host=MILVUS_HOST, port=MILVUS_PORT)

def get_collection():
    return Collection(COLLECTION_NAME)

def build_filter_expr(doc_type: Optional[str], date_from: Optional[str], date_to: Optional[str], min_citations: Optional[int]) -> Optional[str]:
    conditions = []
    
    if doc_type and doc_type in ["Patent", "Research Paper"]:
        conditions.append(f"doc_type == '{doc_type}'")
    
    if date_from:
        conditions.append(f"publication_date >= '{date_from}'")
    
    if date_to:
        conditions.append(f"publication_date <= '{date_to}'")
        
    if min_citations is not None and min_citations > 0:
        conditions.append(f"citation_count >= {min_citations}")
        
    return " and ".join(conditions) if conditions else None

def search_documents(query_vector: list[float], limit: int = 50, filters: Optional[str] = None) -> list[dict]:
    collection = get_collection()
    collection.load()
    
    search_params = {
        "metric_type": "L2",
        "params": {"nprobe": 10},
    }
    
    results = collection.search(
        data=[query_vector],
        anns_field="embedding",
        param=search_params,
        limit=limit,
        expr=filters,
        output_fields=["doc_id", "title", "abstract", "doc_type", "publication_date", "citation_count"]
    )
    
    docs = []
    if len(results) > 0:
        for match in results[0]:
            doc = {
                "id": match.id,
                "distance": match.distance,
                "doc_id": match.entity.get("doc_id"),
                "title": match.entity.get("title"),
                "abstract": match.entity.get("abstract"),
                "doc_type": match.entity.get("doc_type"),
                "publication_date": match.entity.get("publication_date"),
                "citation_count": match.entity.get("citation_count")
            }
            docs.append(doc)
            
    return docs
