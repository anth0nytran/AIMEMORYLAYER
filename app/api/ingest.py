from typing import List, Literal, Optional

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.services.embeddings import embed_text
from app.services.pinecone_client import upsert_vectors
from app.utils.settings import get_settings

class IngestItem(BaseModel):
	text: str
	role: Optional[Literal["user", "assistant"]] = Field(default="user")


class IngestRequest(BaseModel):
	user_id: str
	items: List[IngestItem]


class IngestResponse(BaseModel):
	upserted: int


router = APIRouter(prefix="/ingest", tags=["ingest"])


@router.post("", response_model=IngestResponse)
async def ingest_endpoint(payload: IngestRequest) -> IngestResponse:
	settings = get_settings()
	vectors = []
	for item in payload.items:
		vec = embed_text(item.text)
		vid = f"{payload.user_id}:{item.role}:{hash(item.text)}"
		vectors.append((vid, vec, {"user_id": payload.user_id, "role": item.role, "text": item.text}))
	upsert_vectors(vectors=vectors, namespace=payload.user_id)
	return IngestResponse(upserted=len(vectors))


