import logging

from .schema_manifest import VIEW_DOCUMENTS, get_view_schema, MINIMAL_SCHEMA

logger = logging.getLogger(__name__)


def retrieve_schema_context(question: str, n_results: int = 3) -> str:
    """Retrieve relevant schema views using ChromaDB with fallback."""
    try:
        from .embedder import get_collection
        collection = get_collection()
        results = collection.query(
            query_texts=[question],
            n_results=n_results,
        )
        if results and results["ids"] and results["ids"][0]:
            matched_ids = results["ids"][0]
            distances = results["distances"][0] if results.get("distances") else [0.0]
            best_distance = min(distances)

            # threshold: 0.0 = perfect match, higher = worse match
            if best_distance > 1.2:
                logger.info("ChromaDB best distance %.2f > 1.2, using minimal schema", best_distance)
                return _build_with_minimal(question, matched_ids)

            logger.info("ChromaDB matched %s for question", matched_ids)
            schema = get_view_schema(matched_ids)
            return schema

    except Exception as exc:
        logger.warning("ChromaDB query failed: %s. Falling back to full schema.", exc)

    # fallback: return minimal view listing
    return MINIMAL_SCHEMA


def _build_with_minimal(question: str, matched_ids: list[str]) -> str:
    """Build schema from matched views + fallback note."""
    valid = [vid for vid in matched_ids if any(d["id"] == vid for d in VIEW_DOCUMENTS)]
    if valid:
        return f"{MINIMAL_SCHEMA}\n\nSuggested views: {', '.join(f'welldata.{v}' for v in valid)}"
    return MINIMAL_SCHEMA
