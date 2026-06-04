from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    gemini_api_key: str
    oracle_host: str = "oracle-db"
    oracle_port: int = 1521
    oracle_service: str = "XEPDB1"
    oracle_user: str = "welldata"
    oracle_pwd: str = "Oracle123"
    chroma_path: str = "./chroma_db"
    embed_model: str = "all-MiniLM-L6-v2"
    gemini_model: str = "gemini-flash-latest"
    max_rows: int = 500

    class Config:
        env_file = ".env"

settings = Settings()
