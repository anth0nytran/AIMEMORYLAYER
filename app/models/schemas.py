from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional


class ChatRequest(BaseModel):
	user_id: str = Field(..., description="Unique ID per user/session")
	message: str = Field(..., description="User's input message")
	top_k: int = Field(5, ge=1, le=50, description="Number of memories to retrieve")
	metadata: Optional[Dict[str, Any]] = Field(default=None, description="Optional metadata, e.g., conversation_id")


class RetrievedContextItem(BaseModel):
	text: str
	score: Optional[float] = None
	ts: Optional[str] = None
	role: Optional[str] = Field(default=None, description='"user" | "assistant"')


class UsageInfo(BaseModel):
	prompt_tokens: Optional[int] = 0
	completion_tokens: Optional[int] = 0
	model: Optional[str] = None


class ChatResponse(BaseModel):
	response: str
	context: List[RetrievedContextItem] = []
	usage: Optional[UsageInfo] = None
	latency_ms: Optional[int] = None


class HealthResponse(BaseModel):
	status: str
	pinecone: Optional[str] = None
	hf: Optional[str] = None
	version: Optional[str] = None


