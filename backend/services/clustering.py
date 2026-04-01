import pandas as pd
from sklearn.cluster import KMeans
from services.embedding import get_embedding

def cluster_results(results: list[dict], n_clusters: int = 5) -> dict:
    if not results:
        return {"results": [], "trends": []}
        
    # We will compute embeddings for the matched abstracts to cluster them on the fly
    # Alternatively, we could have retrieved the embeddings from Milvus, but encoding again is fine for N=50
    abstracts = [doc.get("abstract", "") for doc in results]
    
    from sentence_transformers import SentenceTransformer
    # Since model is already loaded in embedding service, we import it directly
    from services.embedding import model
    
    embeddings = model.encode(abstracts)
    
    # Simple KMeans clustering
    actual_clusters = min(n_clusters, len(results))
    kmeans = KMeans(n_clusters=actual_clusters, random_state=42, n_init=10)
    labels = kmeans.fit_predict(embeddings)
    
    sub_topic_labels = {}
    for i, label in enumerate(labels):
        cluster_id = int(label)
        sub_topic = f"Topic {cluster_id + 1}"
        results[i]["sub_topic"] = sub_topic
        if cluster_id not in sub_topic_labels:
            sub_topic_labels[cluster_id] = sub_topic
            
    # Calculate Velocity & Trends
    # We will build a trend map based on publication_date (years) per sub_topic
    trend_data = []
    
    df = pd.DataFrame(results)
    # Extract year from publication_date (format YYYY-MM-DD)
    df['year'] = pd.to_datetime(df['publication_date'], errors='coerce').dt.year
    df['year'] = df['year'].fillna(2020).astype(int)
    
    # Group by Sub-topic and Year
    yearly_counts = df.groupby(['sub_topic', 'year']).size().reset_index(name='count')
    
    # Format for frontend visualization
    for topic in df['sub_topic'].unique():
        topic_data = yearly_counts[yearly_counts['sub_topic'] == topic].sort_values('year')
        trend_data.append({
            "topic": topic,
            "years": topic_data['year'].tolist(),
            "counts": topic_data['count'].tolist(),
            "velocity": float(topic_data['count'].diff().fillna(0).mean()) # Simple velocity: mean growth
        })
        
    return {
        "results": results,
        "trends": trend_data
    }
