import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
from config import settings

_collection = None


def get_collection():
    global _collection
    if _collection is None:
        from .embedder import build_vector_store
        _collection = build_vector_store()
    return _collection


def retrieve_schema_context(question: str, n_results: int = 3) -> str:
    """
    Given a natural language question, retrieve the top-n most relevant
    view descriptions from ChromaDB. Returns a single string ready to
    inject into the LLM prompt.
    """
    collection = get_collection()
    results = collection.query(
        query_texts=[question],
        n_results=min(n_results, collection.count())
    )
    documents = results["documents"][0]
    return "\n\n---\n\n".join(documents)
