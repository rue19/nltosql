from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Gemini (primary LLM)
    gemini_api_key: str = ""
    gemini_model: str = "gemini-1.5-flash"

    # Oracle DB
    oracle_host: str = "oracle-db"
    oracle_port: int = 1521
    oracle_service: str = "XEPDB1"
    oracle_user: str = "welldata"
    oracle_pwd: str = "Oracle123"

    # Qwen local LLM (optional fallback)
    use_local_llm: bool = False
    qwen_model_path: str = "/app/models/qwen2.5-0.5b-instruct-q4_k_m.gguf"
    qwen_context_length: int = 4096
    qwen_max_tokens: int = 512
    qwen_temperature: float = 0.0

    # App settings
    max_rows: int = 500

    class Config:
        env_file = ".env"


settings = Settings()
