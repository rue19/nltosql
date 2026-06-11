import logging
import os
import chromadb

from .schema_manifest import VIEW_DOCUMENTS

logger = logging.getLogger(__name__)

CHROMA_DIR = os.environ.get("CHROMA_DIR", "/app/chroma_db")
COLLECTION_NAME = "schema_views"


def build_vector_store():
    """Build or load the ChromaDB vector store from schema manifest.
    Uses ChromaDB's built-in ONNX embedding (all-MiniLM-L6-v2) - no PyTorch needed.
    """
    os.makedirs(CHROMA_DIR, exist_ok=True)

    client = chromadb.PersistentClient(path=CHROMA_DIR)

    try:
        collection = client.get_collection(name=COLLECTION_NAME)
        count = collection.count()
        logger.info("ChromaDB collection '%s' exists with %s documents", COLLECTION_NAME, count)
        if count >= len(VIEW_DOCUMENTS):
            return collection
        logger.info("Collection stale (has %s, need %s). Rebuilding...", count, len(VIEW_DOCUMENTS))
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        logger.info("Creating new ChromaDB collection '%s'", COLLECTION_NAME)

    collection = client.create_collection(name=COLLECTION_NAME)

    ids = [d["id"] for d in VIEW_DOCUMENTS]
    documents = [d["text"] for d in VIEW_DOCUMENTS]
    metadatas = [d["metadata"] for d in VIEW_DOCUMENTS]

    collection.add(ids=ids, documents=documents, metadatas=metadatas)

    logger.info("ChromaDB: indexed %s view documents", len(ids))
    return collection


def get_collection():
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    return client.get_collection(name=COLLECTION_NAME)
