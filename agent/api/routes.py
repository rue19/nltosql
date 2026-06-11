from fastapi import APIRouter
from sqlalchemy import text

from .models import HealthResponse, QueryRequest, QueryResponse
from agent.chart_advisor import advise_chart
from agent.executor import get_engine, run_query
from agent.nl2sql import generate_sql
from rag.schema_manifest import VIEWS_LIST

router = APIRouter()


@router.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    try:
        sql, _ = generate_sql(request.question)
    except ValueError as e:
        return QueryResponse(
            question=request.question,
            sql="",
            columns=[],
            rows=[],
            row_count=0,
            error=str(e),
        )
    try:
        result = run_query(sql)
    except Exception as e:
        return QueryResponse(
            question=request.question,
            sql=sql,
            columns=[],
            rows=[],
            row_count=0,
            error=f"SQL execution error: {str(e)}",
        )
    chart = advise_chart(result["columns"], result["rows"], request.question)
    return QueryResponse(
        question=request.question,
        sql=sql,
        columns=result["columns"],
        rows=result["rows"],
        row_count=result["row_count"],
        chart_advice=chart,
    )


@router.get("/health", response_model=HealthResponse)
async def health():
    db_ok = False
    try:
        engine = get_engine()
        with engine.connect() as conn:
            conn.execute(text("SELECT 1 FROM DUAL"))
        db_ok = True
    except Exception:
        pass
    # RAG is always ready now: no ChromaDB needed.
    return HealthResponse(status="ok", db_connected=db_ok, rag_ready=True)


@router.get("/views")
async def list_views():
    return VIEWS_LIST
