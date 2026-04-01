import os
import traceback
from pymilvus import connections, Collection, DataType

MILVUS_HOST = os.getenv("MILVUS_HOST", "localhost")
MILVUS_PORT = os.getenv("MILVUS_PORT", "19530")
COLLECTION_NAME = "documents"

def test_filter(expr_label, expr_str):
    print(f"\n--- Testing: {expr_label} ---")
    print(f"Expression: {expr_str}")
    try:
        connections.connect("default", host=MILVUS_HOST, port=MILVUS_PORT)
        collection = Collection(COLLECTION_NAME)
        collection.load()
        
        # Simple search with 10 zeros vector
        results = collection.search(
            data=[[0.0] * 384],
            anns_field="embedding",
            param={"metric_type": "L2", "params": {"nprobe": 10}},
            limit=5,
            expr=expr_str,
            output_fields=["doc_id", "title", "abstract", "doc_type", "publication_date", "citation_count"]
        )
        print(f"✅ SUCCESS: Found {len(results[0])} results.")
        return True
    except Exception as e:
        print(f"❌ FAILED: {type(e).__name__} - {str(e)}")
        # traceback.print_exc()
        return False

if __name__ == "__main__":
    tests = [
        ("None (Base Case)", None),
        ("Doc Type (Single Quotes)", "doc_type == 'Patent'"),
        ("Doc Type (Double Quotes)", 'doc_type == "Patent"'),
        ("Pub Date (Single Quotes)", "publication_date >= '2020-01-01'"),
        ("Pub Date (Double Quotes)", 'publication_date >= "2020-01-01"'),
        ("Citation Count (Int)", "citation_count >= 1"),
        ("Combined (&& and Single)", "doc_type == 'Patent' && publication_date >= '2020-01-01'"),
        ("Combined (and and Single)", "doc_type == 'Patent' and publication_date >= '2020-01-01'"),
        ("Combined (Parentheses)", "(doc_type == 'Patent') and (citation_count >= 1)"),
    ]
    
    results = []
    for label, expr in tests:
        results.append((label, test_filter(label, expr)))
    
    print("\n\n--- DIAGNOSTIC SUMMARY ---")
    for label, success in results:
        status = "PASSED" if success else "FAILED"
        print(f"{label:40} : {status}")
