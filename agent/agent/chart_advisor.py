import json
import logging

from config import settings

logger = logging.getLogger(__name__)

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


def _advise_with_gemini(columns: list, rows: list, question: str) -> dict:
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain.prompts import ChatPromptTemplate
    from langchain.schema.output_parser import StrOutputParser

    llm = ChatGoogleGenerativeAI(
        model=settings.gemini_model,
        google_api_key=settings.gemini_api_key,
        temperature=0.0,
    )
    prompt = ChatPromptTemplate.from_messages([("human", ADVISOR_PROMPT)])
    chain = prompt | llm | StrOutputParser()

    raw = chain.invoke({
        "columns": columns,
        "sample_rows": rows[:5],
        "question": question,
    })
    raw = raw.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
    return json.loads(raw)


def _advise_with_qwen(columns: list, rows: list, question: str) -> dict:
    try:
        from llama_cpp import Llama
    except ImportError as exc:
        raise RuntimeError("llama-cpp-python not installed.") from exc

    llm = Llama(
        model_path=settings.qwen_model_path,
        n_ctx=settings.qwen_context_length,
        n_threads=4,
        verbose=False,
    )

    prompt_text = ADVISOR_PROMPT.format(
        columns=columns,
        sample_rows=rows[:5],
        question=question,
    )

    response = llm.create_chat_completion(
        messages=[{"role": "user", "content": prompt_text}],
        max_tokens=settings.qwen_max_tokens,
        temperature=settings.qwen_temperature,
        stop=["```", "\n\n"],
    )
    raw = response["choices"][0]["message"]["content"]
    raw = raw.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
    return json.loads(raw)


def advise_chart(columns: list, rows: list, question: str) -> dict:
    if not rows:
        return {"chart_type": "none"}
    try:
        if settings.use_local_llm:
            return _advise_with_qwen(columns, rows, question)
        return _advise_with_gemini(columns, rows, question)
    except Exception as exc:
        logger.warning("Chart advisor failed: %s", exc)
        return {"chart_type": "none"}
