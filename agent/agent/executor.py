import oracledb
from sqlalchemy import create_engine, text
from sqlalchemy.pool import NullPool
from config import settings
from typing import Any


def get_engine():
    dsn = (
        f"oracle+oracledb://{settings.oracle_user}:{settings.oracle_pwd}"
        f"@{settings.oracle_host}:{settings.oracle_port}/?service_name={settings.oracle_service}"
    )
    return create_engine(dsn, poolclass=NullPool)


def run_query(sql: str) -> dict[str, Any]:
    """
    Execute a SQL SELECT statement.
    Returns {"columns": [...], "rows": [...], "row_count": int}.
    Raises on non-SELECT statements (safety guard).
    """
    clean = sql.strip().upper()
    if not clean.startswith("SELECT"):
        raise ValueError("Only SELECT statements are permitted.")

    engine = get_engine()
    with engine.connect() as conn:
        result = conn.execute(text(sql))
        columns = list(result.keys())
        rows = [list(row) for row in result.fetchmany(settings.max_rows)]

    return {
        "columns": columns,
        "rows": rows,
        "row_count": len(rows)
    }
