from functools import lru_cache
from typing import List, Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
	model_config = SettingsConfigDict(env_file=(".env",), env_file_encoding="utf-8", extra="ignore")

	# App
	app_name: str = "AI Memory Layer MVP"
	log_level: str = Field(default="info", alias="LOG_LEVEL")
	port: int = Field(default=8000, alias="PORT")

	# CORS
	cors_origins: List[str] = Field(default_factory=lambda: ["http://localhost:7860", "http://localhost:8000"])  # gradio + api

	# HF
	hf_token: Optional[str] = Field(default=None, alias="HF_TOKEN")
	hf_llm_model: str = Field(default="mistralai/Mistral-7B-Instruct-v0.2", alias="HF_LLM_MODEL")
	hf_embedding_model: str = Field(default="sentence-transformers/all-MiniLM-L6-v2", alias="HF_EMBEDDING_MODEL")

	# Pinecone
	pinecone_api_key: Optional[str] = Field(default=None, alias="PINECONE_API_KEY")
	pinecone_index: str = Field(default="ai-memory-mvp", alias="PINECONE_INDEX")
	pinecone_region: Optional[str] = Field(default="us-east-1", alias="PINECONE_REGION")

	# Retrieval
	top_k: int = Field(default=5, ge=1, le=50, alias="TOP_K")

	# Rate limiting (requests per minute)
	rate_limit_rpm: int = Field(default=60, alias="RATE_LIMIT_RPM")

	@field_validator("cors_origins", mode="before")
	@classmethod
	def _split_origins(cls, v):  # type: ignore[no-untyped-def]
		if isinstance(v, str):
			# Support comma-separated string in env var CORS_ORIGINS
			return [s.strip() for s in v.split(",") if s.strip()]
		return v


@lru_cache(maxsize=1)
def get_settings() -> Settings:
	return Settings()


