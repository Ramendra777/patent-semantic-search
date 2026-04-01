from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from services.embedding import get_embedding
from services.milvus import search_documents, build_filter_expr
from services.clustering import cluster_results

router = APIRouter()

@router.get("/search")
def search(
    query: str,
    doc_type: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    min_citations: Optional[int] = None,
):
    try:
        if not query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
            
        vector = get_embedding(query)
        
        # Build filter expression from all provided filters
        filters = build_filter_expr(
            doc_type=doc_type,
            date_from=date_from,
            date_to=date_to,
            min_citations=min_citations,
        )
            
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

