import pandas as pd
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

def extract_cluster_label(abstracts: list[str], top_n: int = 3) -> str:
    """Extract the top TF-IDF keywords from a list of abstracts to name a cluster."""
    if not abstracts:
        return "General"
    try:
        vectorizer = TfidfVectorizer(
            max_features=50,
            stop_words='english',
            max_df=0.95,
            min_df=1
        )
        tfidf_matrix = vectorizer.fit_transform(abstracts)
        feature_names = vectorizer.get_feature_names_out()
        # Average TF-IDF scores across all docs in the cluster
        mean_scores = tfidf_matrix.mean(axis=0).A1
        top_indices = mean_scores.argsort()[-top_n:][::-1]
        keywords = [feature_names[i].capitalize() for i in top_indices]
        return ", ".join(keywords)
    except Exception:
        return "General"

def cluster_results(results: list[dict], n_clusters: int = 5) -> dict:
    if not results:
        return {"results": [], "trends": []}
        
    abstracts = [doc.get("abstract", "") for doc in results]
    
    # Import model from embedding service (already loaded in memory)
    from services.embedding import model
    
    embeddings = model.encode(abstracts)
    
    # KMeans clustering
    actual_clusters = min(n_clusters, len(results))
    if actual_clusters < 2:
        for r in results:
            r["sub_topic"] = "General"
        return {"results": results, "trends": []}

    kmeans = KMeans(n_clusters=actual_clusters, random_state=42, n_init=10)
    labels = kmeans.fit_predict(embeddings)
    
    # Group abstracts by cluster to extract meaningful names
    cluster_abstracts: dict[int, list[str]] = {}
    for i, label in enumerate(labels):
        cluster_id = int(label)
        cluster_abstracts.setdefault(cluster_id, []).append(abstracts[i])
    
    # Generate meaningful names for each cluster using TF-IDF keywords
    cluster_names: dict[int, str] = {}
    for cluster_id, cluster_abs in cluster_abstracts.items():
        cluster_names[cluster_id] = extract_cluster_label(cluster_abs)
    
    # Assign sub-topic names to results
    for i, label in enumerate(labels):
        results[i]["sub_topic"] = cluster_names[int(label)]
            
    # Calculate Velocity & Trends by sub-topic and year
    trend_data = []
    
    df = pd.DataFrame(results)
    df['year'] = pd.to_datetime(df['publication_date'], errors='coerce').dt.year
    df['year'] = df['year'].fillna(2020).astype(int)
    
    yearly_counts = df.groupby(['sub_topic', 'year']).size().reset_index(name='count')
    
    for topic in df['sub_topic'].unique():
        topic_data = yearly_counts[yearly_counts['sub_topic'] == topic].sort_values('year')
        trend_data.append({
            "topic": topic,
            "years": topic_data['year'].tolist(),
            "counts": topic_data['count'].tolist(),
            "velocity": float(topic_data['count'].diff().fillna(0).mean())
        })
        
    return {
        "results": results,
        "trends": trend_data
    }

