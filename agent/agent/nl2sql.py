import logging
import re
import time

from config import settings
from rag.schema_manifest import get_schema_context

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are an expert Oracle SQL query generator for an oil and gas well database.

TASK: Convert the user's natural language question into a single valid Oracle SQL SELECT statement.

RULES:
1. Use ONLY the views listed in the SCHEMA below. Never query base tables directly.
2. Return ONLY the SQL query. No explanation, no markdown, no code fences, no backticks.
3. All view names must be prefixed: welldata.V_VIEW_NAME
4. Use FETCH FIRST 500 ROWS ONLY unless user asks for all rows.
5. Use Oracle syntax: FETCH FIRST not LIMIT, NVL not COALESCE, TO_DATE for dates.
6. For cross-view queries join on UWI = UWI, UBHI = UBHI, or UWI = UBHI.
7. Always use table aliases and qualify all column names.
8. If the question cannot be answered from the available views, respond with exactly:
   CANNOT_ANSWER: <reason in one sentence>

{schema}
"""


def _clean_sql(raw: str) -> str:
    """Strip markdown fencing and whitespace from LLM output, and fix LIMIT syntax."""
    raw = raw.strip()
    raw = re.sub(r"^```sql\s*", "", raw, flags=re.IGNORECASE)
    raw = re.sub(r"^```\s*", "", raw, flags=re.IGNORECASE)
    raw = re.sub(r"\s*```$", "", raw)
    
    # Robustly fix LIMIT hallucinations since local models often ignore prompt instructions for Oracle syntax
    raw = re.sub(r"\bLIMIT\s+(\d+)\b", r"FETCH FIRST \1 ROWS ONLY", raw, flags=re.IGNORECASE)
    
    return raw.strip()


def _generate_with_gemini(question: str, schema: str) -> str:
    """Call Gemini API with exponential backoff on quota errors."""
    from google.api_core.exceptions import ResourceExhausted
    from langchain.prompts import ChatPromptTemplate
    from langchain.schema.output_parser import StrOutputParser
    from langchain_google_genai import ChatGoogleGenerativeAI

    llm = ChatGoogleGenerativeAI(
        model=settings.gemini_model,
        google_api_key=settings.gemini_api_key,
        temperature=0.0,
        max_retries=0,
    )
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT.format(schema=schema)),
        ("human", "{question}"),
    ])
    chain = prompt | llm | StrOutputParser()

    last_error = None
    for attempt, wait in enumerate([0, 10, 20, 40]):
        if wait > 0:
            logger.warning("Gemini quota hit. Waiting %ss (attempt %s/4)...", wait, attempt + 1)
            time.sleep(wait)
        try:
            return chain.invoke({"question": question})
        except ResourceExhausted as e:
            last_error = e
            logger.warning("Gemini ResourceExhausted on attempt %s: %s", attempt + 1, e)
        except Exception:
            raise

    raise last_error


def _generate_with_qwen(question: str, schema: str) -> str:
    """Call local Qwen GGUF model via llama-cpp-python."""
    try:
        from llama_cpp import Llama
    except ImportError as exc:
        raise RuntimeError("llama-cpp-python not installed. Cannot use local LLM.") from exc

    llm = Llama(
        model_path=settings.qwen_model_path,
        n_ctx=settings.qwen_context_length,
        n_threads=4,
        verbose=False,
    )

    system_content = SYSTEM_PROMPT.format(schema=schema)
    messages = [
        {"role": "system", "content": system_content},
        {"role": "user", "content": question},
    ]

    response = llm.create_chat_completion(
        messages=messages,
        max_tokens=settings.qwen_max_tokens,
        temperature=settings.qwen_temperature,
        stop=["```", "\n\n\n"],
    )
    return response["choices"][0]["message"]["content"]


def generate_sql(question: str) -> tuple[str, str]:
    """
    Generate Oracle SQL from a natural language question.
    Returns (sql_query, schema_context_used).
    Raises ValueError if the model returns CANNOT_ANSWER.
    """
    schema = get_schema_context(question)

    if settings.use_local_llm:
        logger.info("Using local Qwen model for SQL generation")
        raw = _generate_with_qwen(question, schema)
    else:
        logger.info("Using Gemini API for SQL generation")
        raw = _generate_with_gemini(question, schema)

    sql = _clean_sql(raw)

    if sql.upper().startswith("CANNOT_ANSWER"):
        raise ValueError(sql)

    return sql, schema
