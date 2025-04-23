from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict


class Settings(BaseSettings):
    # PINECONE_API_KEY: str # Removed
    GROQ_API_KEY: str
    OPENAI_API_KEY: str
    QDRANT_API_KEY: str
    QDRANT_URL: str
    QDRANT_COLLECTION_NAME: str

    model_config = SettingsConfigDict(env_file='.env')


settings = Settings()
