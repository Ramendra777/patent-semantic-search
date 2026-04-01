try:
    from services.milvus import get_collection, build_filter_expr, search_documents
    from services.embedding import get_embedding
    from services.clustering import cluster_results
    import traceback
    
    collection = get_collection()
    print(f"Collection Loaded: {collection.is_empty == False}")
    print(f"Num Entities: {collection.num_entities}")
    
    query = "machine learning"
    doc_type = "Patent"
    date_from = "2026-01-01"
    date_to = "2026-04-01"
    min_citations = 5
    
    print(f"Searching for: {query} with filters: {doc_type}, {date_from}, {date_to}, {min_citations}")
    
    vector = get_embedding(query)
    filters = build_filter_expr(doc_type, date_from, date_to, min_citations)
    print(f"Generated Filter Expression: {filters}")
    
    print("Executing search...")
    results = search_documents(query_vector=vector, limit=50, filters=filters)
    print(f"Search successful! Found {len(results)} results.")
    
    if results:
        print("Executing clustering...")
        clustered = cluster_results(results)
        print("Clustering successful!")
    
except Exception as e:
    print("\n--- ERROR DETECTED ---")
    print(f"Exception Type: {type(e).__name__}")
    print(f"Exception Message: {str(e)}")
    traceback.print_exc()
