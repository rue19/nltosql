from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from config import settings
import json

llm = ChatGoogleGenerativeAI(
    model=settings.gemini_model,
    google_api_key=settings.gemini_api_key,
    temperature=0.0,
)

ADVISOR_PROMPT = """You are a data visualization advisor.
Given the column names and a sample of data rows from a SQL query result,
suggest the best chart type and configuration.

Return ONLY valid JSON in this exact format:
{
  "chart_type": "bar" | "line" | "scatter" | "pie" | "none",
  "x_column": "column_name_for_x_axis",
  "y_column": "column_name_for_y_axis",
  "title": "suggested chart title",
  "reason": "one sentence explaining the choice"
}

If the data is not suitable for a chart (e.g. a single row, text-only columns), use "none".

Columns: {columns}
Sample rows (first 5): {sample_rows}
Original question: {question}
"""

prompt = ChatPromptTemplate.from_messages([
    ("human", ADVISOR_PROMPT)
])

chain = prompt | llm | StrOutputParser()


def advise_chart(columns: list, rows: list, question: str) -> dict:
    if not rows:
        return {"chart_type": "none"}
    try:
        raw = chain.invoke({
            "columns": columns,
            "sample_rows": rows[:5],
            "question": question
        })
        raw = raw.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
        return json.loads(raw)
    except Exception:
        return {"chart_type": "none"}
