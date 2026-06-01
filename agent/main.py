from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router
from rag.embedder import build_vector_store

app = FastAPI(title="NL2SQL Agent", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")

@app.on_event("startup")
async def startup():
    build_vector_store()  # no-op if already built
