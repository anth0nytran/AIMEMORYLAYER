from fastapi import APIRouter

from app.models.schemas import ChatRequest, ChatResponse, RetrievedContextItem
from app.services.embeddings import embed_text
from app.services.pinecone_client import query_top_k
from app.utils.settings import get_settings
from app.services.llm import generate_response


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
	# Build a simple prompt with retrieved context
	context_block = "\n".join([f"- ({c.role}) {c.text}" for c in context_items])
	system = "You are a helpful assistant. Use the provided memory snippets if relevant."
	prompt = f"{system}\n\nMemory:\n{context_block}\n\nUser: {payload.message}\nAssistant:"
	resp_text = generate_response(prompt)
	return ChatResponse(response=resp_text, context=context_items, usage=None, latency_ms=None)


