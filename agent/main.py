import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router
from rag.embedder import build_vector_store

logger = logging.getLogger(__name__)

app = FastAPI(title="NL2SQL Agent", version="3.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")


@app.on_event("startup")
async def startup():
    logger.info("Building ChromaDB vector store from schema manifest...")
    try:
        build_vector_store()
        logger.info("ChromaDB vector store ready.")
    except Exception as exc:
        logger.warning("ChromaDB build failed: %s. Falling back to full schema.", exc)
