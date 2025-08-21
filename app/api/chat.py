from fastapi import APIRouter

from app.models.schemas import ChatRequest, ChatResponse, RetrievedContextItem
from app.services.embeddings import embed_text
from app.services.pinecone_client import query_top_k, upsert_vectors, rerank_by_recency_and_score
from app.utils.settings import get_settings
from app.services.llm import generate_response
from datetime import datetime, timezone
from uuid import uuid4


router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def chat_endpoint(payload: ChatRequest) -> ChatResponse:
	settings = get_settings()
	query_vec = embed_text(payload.message)

	# Upsert the user's message as memory
	user_vector_id = f"{payload.user_id}:user:{uuid4()}"
	user_meta = {"user_id": payload.user_id, "role": "user", "text": payload.message, "ts": datetime.now(timezone.utc).isoformat()}
	upsert_vectors(vectors=[(user_vector_id, query_vec, user_meta)], namespace=payload.user_id)
	res = query_top_k(vector=query_vec, top_k=payload.top_k, namespace=payload.user_id)
	# Apply recency-biased rerank
	matches = rerank_by_recency_and_score(getattr(res, "matches", []))
	context_items = []
	for match in matches:
		meta = match.metadata or {}
		context_items.append(RetrievedContextItem(text=meta.get("text", ""), score=getattr(match, "score", None), role=meta.get("role")))
	# Build a simple prompt with retrieved context
	context_block = "\n".join([f"- ({c.role}) {c.text}" for c in context_items])
	system = "You are a helpful assistant. Use the provided memory snippets if relevant."
	prompt = f"{system}\n\nMemory:\n{context_block}\n\nUser: {payload.message}\nAssistant:"
	resp_text = generate_response(prompt)

	# Store assistant response for future retrieval
	assistant_vec = embed_text(resp_text)
	assistant_vector_id = f"{payload.user_id}:assistant:{uuid4()}"
	assistant_meta = {"user_id": payload.user_id, "role": "assistant", "text": resp_text, "ts": datetime.now(timezone.utc).isoformat()}
	upsert_vectors(vectors=[(assistant_vector_id, assistant_vec, assistant_meta)], namespace=payload.user_id)
	return ChatResponse(response=resp_text, context=context_items, usage=None, latency_ms=None)


