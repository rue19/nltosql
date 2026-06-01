from fastapi import APIRouter
from .models import QueryRequest, QueryResponse, HealthResponse
from agent.nl2sql import generate_sql
from agent.executor import run_query, get_engine
from agent.chart_advisor import advise_chart
from rag.retriever import get_collection
from sqlalchemy import text

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
            error=str(e)
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
            error=f"SQL execution error: {str(e)}"
        )

    chart = advise_chart(result["columns"], result["rows"], request.question)

    return QueryResponse(
        question=request.question,
        sql=sql,
        columns=result["columns"],
        rows=result["rows"],
        row_count=result["row_count"],
        chart_advice=chart
    )

@router.get("/health", response_model=HealthResponse)
async def health():
    db_ok = False
    rag_ok = False
    try:
        engine = get_engine()
        with engine.connect() as conn:
            conn.execute(text("SELECT 1 FROM DUAL"))
        db_ok = True
    except Exception:
        pass
    try:
        col = get_collection()
        rag_ok = col.count() > 0
    except Exception:
        pass
    return HealthResponse(status="ok", db_connected=db_ok, rag_ready=rag_ok)

@router.get("/views")
async def list_views():
    from rag.schema_manifest import VIEWS
    return [{"view_name": v["view_name"], "description": v["description"]} for v in VIEWS]
