"""
Clustering and extractive summarization using TF-IDF + KMeans
"""
import re
from typing import List, Dict, Optional, Tuple
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from schemas import Chunk, Cluster, Citation, CitationSpan


def extract_sentences(text: str) -> List[str]:
    """Extract sentences from text"""
    # Simple sentence splitting
    sentences = re.split(r'[.!?]+\s+', text)
    return [s.strip() for s in sentences if s.strip()]


def textrank_sentences(sentences: List[str], top_n: int = 3) -> List[str]:
    """Simple TextRank-style sentence ranking based on TF-IDF similarity"""
    if len(sentences) <= top_n:
        return sentences
    
    # Create TF-IDF vectors for sentences
    vectorizer = TfidfVectorizer(max_features=100, stop_words='english')
    try:
        sentence_vectors = vectorizer.fit_transform(sentences)
    except ValueError:
        # Fallback if no valid features
        return sentences[:top_n]
    
    # Compute similarity matrix
    similarity_matrix = (sentence_vectors * sentence_vectors.T).toarray()
    
    # Simple scoring: sum of similarities to other sentences
    scores = similarity_matrix.sum(axis=1)
    
    # Get top N sentences
    top_indices = np.argsort(scores)[-top_n:][::-1]
    return [sentences[i] for i in sorted(top_indices)]


def cluster_chunks(
    chunks: List[Chunk],
    goal: str,
    n_clusters: Optional[int] = None,
    seed: Optional[int] = None
) -> Tuple[List[List[int]], np.ndarray]:
    """
    Cluster chunks using TF-IDF + KMeans
    
    Returns:
        - cluster_assignments: List of lists, each containing chunk indices for that cluster
        - tfidf_matrix: TF-IDF matrix for later use
    """
    if not chunks:
        return [], np.array([])
    
    # Determine number of clusters
    if n_clusters is None:
        n_clusters = min(5, max(2, len(chunks) // 3))
    
    n_clusters = min(n_clusters, len(chunks))
    
    # Extract text from chunks
    texts = [chunk.text for chunk in chunks]
    
    # Create TF-IDF vectors
    vectorizer = TfidfVectorizer(
        max_features=500,
        stop_words='english',
        ngram_range=(1, 2),
        min_df=1,
        max_df=0.95
    )
    
    try:
        tfidf_matrix = vectorizer.fit_transform(texts)
    except ValueError:
        # Fallback: return all chunks in one cluster
        return [[i for i in range(len(chunks))]], np.array([])
    
    # KMeans clustering
    kmeans = KMeans(
        n_clusters=n_clusters,
        random_state=seed,
        n_init=10,
        max_iter=300
    )
    
    cluster_labels = kmeans.fit_predict(tfidf_matrix)
    
    # Group chunks by cluster
    cluster_assignments = [[] for _ in range(n_clusters)]
    for idx, label in enumerate(cluster_labels):
        cluster_assignments[label].append(idx)
    
    return cluster_assignments, tfidf_matrix


def summarize_cluster(
    chunks: List[Chunk],
    chunk_indices: List[int],
    goal: str,
    max_sentences: int = 3
) -> Tuple[str, List[Citation]]:
    """
    Summarize a cluster using extractive summarization
    
    Returns:
        - summary: Extracted summary text
        - citations: List of citations with provenance
    """
    if not chunk_indices:
        return "No content available.", []
    
    # Get chunks for this cluster
    cluster_chunks = [chunks[i] for i in chunk_indices]
    
    # Extract all sentences from cluster chunks
    all_sentences = []
    sentence_to_chunk = []  # Map sentence index to chunk index
    
    for chunk_idx, chunk in enumerate(cluster_chunks):
        sentences = extract_sentences(chunk.text)
        all_sentences.extend(sentences)
        sentence_to_chunk.extend([chunk_idx] * len(sentences))
    
    if not all_sentences:
        return "No extractable content.", []
    
    # Use TextRank to get top sentences
    top_sentences = textrank_sentences(all_sentences, top_n=max_sentences)
    
    # Build summary
    summary = " ".join(top_sentences)
    
    # Build citations with provenance
    citations = []
    cited_chunks = set()
    
    for sentence in top_sentences:
        # Find which chunk this sentence came from
        for idx, s in enumerate(all_sentences):
            if s == sentence:
                chunk_idx = sentence_to_chunk[idx]
                chunk = cluster_chunks[chunk_idx]
                
                if chunk.doc_id not in cited_chunks:
                    # Find sentence position in chunk
                    sentence_start = chunk.text.find(sentence)
                    sentence_end = sentence_start + len(sentence)
                    
                    citations.append(Citation(
                        doc_id=chunk.doc_id,
                        spans=[CitationSpan(
                            chunk_id=chunk.chunk_id,
                            start=sentence_start,
                            end=sentence_end
                        )]
                    ))
                    cited_chunks.add(chunk.doc_id)
                break
    
    # If no citations found, add at least one
    if not citations and cluster_chunks:
        chunk = cluster_chunks[0]
        citations.append(Citation(
            doc_id=chunk.doc_id,
            spans=[CitationSpan(
                chunk_id=chunk.chunk_id,
                start=0,
                end=min(100, len(chunk.text))
            )]
        ))
    
    return summary, citations


def generate_clusters(
    chunks: List[Chunk],
    goal: str,
    n_clusters: Optional[int] = None,
    seed: Optional[int] = None
) -> List[Cluster]:
    """
    Generate clusters from chunks using TF-IDF + KMeans with extractive summarization
    """
    if not chunks:
        return []
    
    # Cluster chunks
    cluster_assignments, _ = cluster_chunks(chunks, goal, n_clusters, seed)
    
    clusters = []
    for cluster_idx, chunk_indices in enumerate(cluster_assignments):
        if not chunk_indices:
            continue
        
        # Summarize cluster
        summary, citations = summarize_cluster(chunks, chunk_indices, goal)
        
        # Generate cluster label based on goal and content
        label = f"Cluster {cluster_idx + 1}"
        if goal:
            # Try to extract a keyword from goal
            goal_words = goal.split()[:3]
            label = f"{' '.join(goal_words)} - {label}"
        
        clusters.append(Cluster(
            label=label,
            summary=summary,
            citations=citations
        ))
    
    return clusters

