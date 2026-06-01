import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
from .schema_manifest import VIEWS, UWI_UBHI_RULE, ORACLE_SYNTAX_RULES
from config import settings
import json


def build_vector_store():
    """
    Builds the ChromaDB collection from VIEWS.
    Each document = one view entry.
    Metadata carries view_name and join_keys for filtering.
    Called once at agent startup if collection does not exist.
    """
    client = chromadb.PersistentClient(path=settings.chroma_path)
    ef = SentenceTransformerEmbeddingFunction(
        model_name=settings.embed_model,
        device="cpu"
    )

    collection = client.get_or_create_collection(
        name="schema_views",
        embedding_function=ef,
        metadata={"hnsw:space": "cosine"}
    )

    if collection.count() > 0:
        return collection

    documents = []
    metadatas = []
    ids = []

    for view in VIEWS:
        col_text = "\n".join(
            f"  - {c['name']} ({c['type']}): {c.get('description', '')}"
            for c in view["columns"]
        )
        examples = "\n".join(
            f"  Q: {q}" for q in view.get("example_questions", [])
        )
        doc = (
            f"VIEW: {view['view_name']}\n"
            f"DESCRIPTION: {view['description']}\n"
            f"COLUMNS:\n{col_text}\n"
            f"JOIN KEYS: {', '.join(view['join_keys'])}\n"
            f"EXAMPLE QUESTIONS:\n{examples}\n"
            f"\n{UWI_UBHI_RULE}\n"
            f"{ORACLE_SYNTAX_RULES}"
        )
        documents.append(doc)
        metadatas.append({
            "view_name": view["view_name"],
            "join_keys": json.dumps(view["join_keys"])
        })
        ids.append(view["view_name"])

    collection.add(documents=documents, metadatas=metadatas, ids=ids)
    return collection
