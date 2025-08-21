from fastapi import APIRouter

from app.models.schemas import ChatRequest, ChatResponse, RetrievedContextItem
from app.services.embeddings import embed_text
from app.services.pinecone_client import query_top_k
from app.utils.settings import get_settings


router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def chat_endpoint(payload: ChatRequest) -> ChatResponse:
	settings = get_settings()
	query_vec = embed_text(payload.message)
	res = query_top_k(vector=query_vec, top_k=payload.top_k, namespace=payload.user_id)
	context_items = []
	for match in res.matches or []:
		meta = match.metadata or {}
		context_items.append(RetrievedContextItem(text=meta.get("text", ""), score=getattr(match, "score", None), role=meta.get("role")))
	# Temporary: echo back with context count; LLM integration to follow
	resp_text = f"Found {len(context_items)} memories. You said: {payload.message}"
	return ChatResponse(response=resp_text, context=context_items, usage=None, latency_ms=None)


