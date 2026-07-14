from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Libris"
    env: str = "development"
    log_level: str = "INFO"

    # Ingestion Configuration
    chunk_size: int = 500
    chunk_overlap: int = 50

    # Retrieval Configuration
    similarity_threshold: float = 0.5
    retrieval_limit: int = 5

    # Storage and Provider Configuration
    chroma_db_path: str = "./data/chroma"
    embedding_model: str = "all-MiniLM-L6-v2"
    gemini_api_key: str = ""


# Globally shared configuration instance
settings = Settings()
