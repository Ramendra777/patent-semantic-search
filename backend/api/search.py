from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from services.embedding import get_embedding
from services.milvus import search_documents
from services.clustering import cluster_results

router = APIRouter()

@router.get("/search")
def search(query: str, doc_type: Optional[str] = None):
    try:
        if not query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
            
        vector = get_embedding(query)
        
        # Build filter expression if doc_type is provided
        filters = None
        if doc_type and doc_type in ["Patent", "Research Paper"]:
            filters = f"doc_type == '{doc_type}'"
            
        results = search_documents(query_vector=vector, limit=50, filters=filters)
        
        clustered_data = cluster_results(results, n_clusters=5)
        
        return {
            "query": query,
            "count": len(clustered_data["results"]),
            "results": clustered_data["results"],
            "trends": clustered_data["trends"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
