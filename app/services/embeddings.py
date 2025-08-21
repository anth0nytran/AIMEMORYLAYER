from typing import List, Optional

import httpx

from app.utils.settings import get_settings


def _hf_headers(token: Optional[str]) -> dict:
	return {"Authorization": f"Bearer {token}"} if token else {}


async def embed_texts_async(texts: List[str]) -> List[List[float]]:
	settings = get_settings()
	model = settings.hf_embedding_model
	headers = _hf_headers(settings.hf_token)
	url = f"https://api-inference.huggingface.co/models/{model}"
	async with httpx.AsyncClient(timeout=60) as client:
		resp = await client.post(url, headers=headers, json={"inputs": texts})
		resp.raise_for_status()
		data = resp.json()
		# If single input, HF may return a single vector; for batch returns list of vectors
		if isinstance(data, list) and len(data) > 0 and isinstance(data[0], list):
			# Heuristic: if first element is float -> single vector
			if len(data) > 0 and all(isinstance(x, (int, float)) for x in data[0]):
				return [data]  # type: ignore[list-item]
		return data  # type: ignore[return-value]


def embed_text(text: str) -> List[float]:
	settings = get_settings()
	model = settings.hf_embedding_model
	headers = _hf_headers(settings.hf_token)
	url = f"https://api-inference.huggingface.co/models/{model}"
	resp = httpx.post(url, headers=headers, json={"inputs": text}, timeout=60)
	resp.raise_for_status()
	data = resp.json()
	# HF returns nested list for sequence of tokens; for sentence transformers it's usually a 1D vector
	if isinstance(data, list) and len(data) > 0 and isinstance(data[0], list):
		# If the first element is a float, it's already a vector
		if all(isinstance(x, (int, float)) for x in data):
			return data  # type: ignore[return-value]
		# Otherwise take first pooling
		return data[0]  # type: ignore[return-value]
	return data  # type: ignore[return-value]


