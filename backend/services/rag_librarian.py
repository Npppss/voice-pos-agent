"""
RAG Librarian — semantic menu matching via vector similarity search.
"""

import chromadb
from sentence_transformers import SentenceTransformer

from config import settings

# Initialize embedding model and ChromaDB client (lazy loaded)
_model: SentenceTransformer | None = None
_collection = None


def _get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(settings.EMBEDDING_MODEL)
    return _model


def _get_collection():
    global _collection
    if _collection is None:
        client = chromadb.HttpClient(
            host=settings.CHROMA_HOST,
            port=settings.CHROMA_PORT,
        )
        _collection = client.get_or_create_collection("menu_items")
    return _collection


# Similarity thresholds
THRESHOLD_AUTO = 0.25       # High confidence — auto-select
THRESHOLD_PROBABLE = 0.45   # Probable — present for validation
# Above 0.45 — low confidence, ask for clarification


async def match_menu_items(query: str, top_k: int = 5) -> list[dict]:
    """
    Search the vector DB for menu items matching the spoken query.

    Args:
        query: Colloquial food name from transcription
        top_k: Number of results to retrieve

    Returns:
        List of matched items sorted by relevance, each containing:
        - product_id, sku, name, category, price, distance
    """
    model = _get_model()
    collection = _get_collection()

    # Encode query with 'query:' prefix for asymmetric retrieval models
    query_embedding = model.encode(f"query: {query}").tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["metadatas", "distances", "documents"],
    )

    matched = []
    if results and results["metadatas"]:
        for i, metadata in enumerate(results["metadatas"][0]):
            distance = results["distances"][0][i]

            # Filter by threshold
            if distance <= THRESHOLD_PROBABLE:
                matched.append({
                    "product_id": metadata.get("product_id"),
                    "sku": metadata.get("sku"),
                    "name": metadata.get("name"),
                    "category": metadata.get("category"),
                    "price": metadata.get("price", 0),
                    "distance": distance,
                    "confidence": "high" if distance <= THRESHOLD_AUTO else "probable",
                })

    return matched
