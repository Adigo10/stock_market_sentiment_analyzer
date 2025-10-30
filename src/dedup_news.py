"""
Deduplicate news articles using sentence-transformer embeddings.
"""

from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.cluster import AgglomerativeClustering

def dedup_news_articles(news: List[Dict[str, Any]], threshold: float = 0.76) -> List[Dict[str, Any]]:
    """
    Deduplicate news articles using clustering on embeddings of headline+summary.
    Articles in the same cluster are considered near-duplicates (same event/topic).
    Only one article per cluster is kept (the first occurrence).
    threshold: float, cosine similarity threshold for clustering (lower = stricter).
    """
    if not news:
        return []
    texts = [
        (str(item.get('headline', '')) + ' ' + str(item.get('summary', ''))).strip()
        for item in news
    ]
    model = SentenceTransformer('all-MiniLM-L6-v2')
    embeddings = model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
    # AgglomerativeClustering uses distance, so convert similarity threshold to distance
    # cosine distance = 1 - cosine similarity
    distance_threshold = 1 - threshold
    clustering = AgglomerativeClustering(
        n_clusters=None,
        metric='cosine',
        linkage='average',
        distance_threshold=distance_threshold
    )
    labels = clustering.fit_predict(embeddings)
    # For each cluster, keep the first article
    seen_clusters = set()
    unique_indices = []
    for idx, label in enumerate(labels):
        if label not in seen_clusters:
            unique_indices.append(idx)
            seen_clusters.add(label)
    return [news[i] for i in unique_indices]

