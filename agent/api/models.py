from pydantic import BaseModel
from typing import Any, Optional

class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    question: str
    sql: str
    columns: list[str]
    rows: list[list[Any]]
    row_count: int
    chart_advice: Optional[dict] = None
    error: Optional[str] = None

class HealthResponse(BaseModel):
    status: str
    db_connected: bool
    rag_ready: bool
