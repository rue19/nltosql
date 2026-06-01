from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from config import settings
from rag.retriever import retrieve_schema_context
import re

llm = ChatGoogleGenerativeAI(
    model=settings.gemini_model,
    google_api_key=settings.gemini_api_key,
    temperature=0.0,
)

SYSTEM_PROMPT = """You are an expert Oracle SQL query generator for an oil and gas well database.

Your task:
1. Read the user's question carefully.
2. Use ONLY the views listed in the SCHEMA CONTEXT below. Never query base tables.
3. Generate a single valid Oracle SQL SELECT statement.
4. Return ONLY the SQL query, nothing else. No explanation, no markdown, no code fences.
5. All view names must be prefixed with the schema: welldata.VIEW_NAME
6. Follow all Oracle syntax rules provided in the schema context.
7. If a question requires data from multiple views, join them on UWI or UBHI as appropriate.
8. Always add a FETCH FIRST 500 ROWS ONLY clause unless the question explicitly asks for all rows.
9. If you cannot answer the question from the available views, return exactly:
   CANNOT_ANSWER: <brief reason>

SCHEMA CONTEXT:
{schema_context}
"""

prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("human", "{question}")
])

chain = prompt | llm | StrOutputParser()


def generate_sql(question: str) -> tuple[str, str]:
    """
    Returns (sql_query, schema_context_used).
    Raises ValueError if the LLM returns CANNOT_ANSWER.
    """
    schema_context = retrieve_schema_context(question, n_results=3)
    raw = chain.invoke({
        "question": question,
        "schema_context": schema_context
    }).strip()

    raw = re.sub(r"^```sql\s*", "", raw, flags=re.IGNORECASE)
    raw = re.sub(r"^```\s*", "", raw, flags=re.IGNORECASE)
    raw = re.sub(r"\s*```$", "", raw)
    raw = raw.strip()

    if raw.upper().startswith("CANNOT_ANSWER"):
        raise ValueError(raw)

    return raw, schema_context
