from fastapi import APIRouter

from app.models.schemas import ChatRequest, ChatResponse


router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def chat_endpoint(payload: ChatRequest) -> ChatResponse:
	# Stub implementation; will be wired to embeddings, Pinecone, and LLM later
	return ChatResponse(response="Hello! Memory pipeline not yet connected.", context=[], usage=None, latency_ms=None)


