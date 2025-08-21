from typing import List, Literal, Optional

from fastapi import APIRouter
from pydantic import BaseModel, Field


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
	# Stub: later will upsert into Pinecone
	return IngestResponse(upserted=len(payload.items))


