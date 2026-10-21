from qdrant_client import QdrantClient
from dotenv import load_dotenv
import os

load_dotenv()

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

_MODEL = None
_QDRANT_AVAILABLE = True

def get_embedding_model():
    global _MODEL
    if _MODEL is None:
        from sentence_transformers import SentenceTransformer
        _MODEL = SentenceTransformer("all-MiniLM-L6-v2")
    return _MODEL

def retrieve_relevant_chunks(query, top_k=5, collection_name="mb_docs"):
    """Retrieve relevant chunks from Qdrant vector database with graceful fallback."""
    global _QDRANT_AVAILABLE
    if not QDRANT_URL or not _QDRANT_AVAILABLE:
        return []

    try:
        model = get_embedding_model()
        query_vector = model.encode(query).tolist()

        qdrant = QdrantClient(
            url=QDRANT_URL,
            api_key=QDRANT_API_KEY,
            timeout=3.0
        )

        results = []
        if hasattr(qdrant, "query_points"):
            response = qdrant.query_points(
                collection_name=collection_name,
                query=query_vector,
                limit=top_k
            )
            points = response.points if hasattr(response, "points") else response
            for hit in points:
                payload = getattr(hit, "payload", {}) or {}
                text = payload.get("text") or payload.get("page_content") or ""
                if text:
                    results.append(text)
            return results
        elif hasattr(qdrant, "search"):
            search_result = qdrant.search(
                collection_name=collection_name,
                query_vector=query_vector,
                limit=top_k
            )
            for hit in search_result:
                payload = getattr(hit, "payload", {}) or {}
                text = payload.get("text") or payload.get("page_content") or ""
                if text:
                    results.append(text)
            return results
    except Exception as e:
        # Fallback gracefully if remote Qdrant DB is unreachable or down
        _QDRANT_AVAILABLE = False
        print(f"Vector search notice: {e}. Continuing with standard debugger context.")

    return []
