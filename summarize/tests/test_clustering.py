"""
Unit tests for clustering and extractive summarization
"""
import pytest
from summarize.clustering import (
    extract_sentences,
    textrank_sentences,
    cluster_chunks,
    summarize_cluster,
    generate_clusters
)
from summarize.schemas import Chunk


def test_extract_sentences():
    """Test sentence extraction"""
    text = "This is sentence one. This is sentence two! Is this sentence three?"
    sentences = extract_sentences(text)
    assert len(sentences) == 3
    assert "sentence one" in sentences[0]
    assert "sentence two" in sentences[1]
    assert "sentence three" in sentences[2]


def test_textrank_sentences():
    """Test TextRank-style sentence ranking"""
    sentences = [
        "Machine learning is a subset of artificial intelligence.",
        "It enables computers to learn from data.",
        "Deep learning uses neural networks.",
        "The weather is nice today.",
        "Natural language processing is important."
    ]
    
    top = textrank_sentences(sentences, top_n=2)
    assert len(top) == 2
    assert all(s in sentences for s in top)


def test_cluster_chunks():
    """Test chunk clustering with TF-IDF + KMeans"""
    chunks = [
        Chunk(chunk_id=0, text="Machine learning and AI are related.", doc_id="doc1", start=0, end=40),
        Chunk(chunk_id=1, text="Deep learning uses neural networks.", doc_id="doc1", start=40, end=80),
        Chunk(chunk_id=2, text="The weather forecast shows rain.", doc_id="doc2", start=0, end=35),
        Chunk(chunk_id=3, text="Today will be sunny and warm.", doc_id="doc2", start=35, end=70),
    ]
    
    cluster_assignments, _ = cluster_chunks(chunks, goal="test", n_clusters=2, seed=42)
    
    assert len(cluster_assignments) == 2
    assert sum(len(c) for c in cluster_assignments) == len(chunks)


def test_summarize_cluster():
    """Test cluster summarization"""
    chunks = [
        Chunk(chunk_id=0, text="Machine learning is important. It helps solve problems.", doc_id="doc1", start=0, end=60),
        Chunk(chunk_id=1, text="AI and ML are transforming industries.", doc_id="doc1", start=60, end=100),
    ]
    
    summary, citations = summarize_cluster(chunks, [0, 1], goal="test", max_sentences=2)
    
    assert len(summary) > 0
    assert len(citations) > 0
    assert citations[0].doc_id == "doc1"
    assert len(citations[0].spans) > 0


def test_generate_clusters():
    """Test full cluster generation"""
    chunks = [
        Chunk(chunk_id=0, text="Machine learning algorithms learn from data.", doc_id="doc1", start=0, end=45),
        Chunk(chunk_id=1, text="Deep learning uses neural networks for complex tasks.", doc_id="doc1", start=45, end=100),
        Chunk(chunk_id=2, text="The weather is sunny today.", doc_id="doc2", start=0, end=30),
        Chunk(chunk_id=3, text="Rain is expected tomorrow.", doc_id="doc2", start=30, end=60),
    ]
    
    clusters = generate_clusters(chunks, goal="test clustering", n_clusters=2, seed=42)
    
    assert len(clusters) > 0
    assert all(cluster.summary for cluster in clusters)
    assert all(cluster.citations for cluster in clusters)
    assert all(c.doc_id for cluster in clusters for c in cluster.citations)


def test_deterministic_clustering():
    """Test that clustering is deterministic with same seed"""
    chunks = [
        Chunk(chunk_id=i, text=f"Document {i} contains important information.", doc_id=f"doc{i}", start=0, end=50)
        for i in range(10)
    ]
    
    clusters1 = generate_clusters(chunks, goal="test", seed=42)
    clusters2 = generate_clusters(chunks, goal="test", seed=42)
    
    # Should produce same number of clusters
    assert len(clusters1) == len(clusters2)
    
    # Labels should match (deterministic)
    labels1 = [c.label for c in clusters1]
    labels2 = [c.label for c in clusters2]
    assert labels1 == labels2

