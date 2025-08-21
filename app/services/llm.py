from typing import Optional

import httpx

from app.utils.settings import get_settings


def _hf_headers(token: Optional[str]) -> dict:
	return {"Authorization": f"Bearer {token}"} if token else {}


def generate_response(prompt: str, max_new_tokens: int = 256, temperature: float = 0.2) -> str:
	settings = get_settings()
	model = settings.hf_llm_model
	headers = _hf_headers(settings.hf_token)
	url = f"https://api-inference.huggingface.co/models/{model}"
	payload = {
		"inputs": prompt,
		"parameters": {
			"max_new_tokens": max_new_tokens,
			"temperature": temperature,
		}
	}
	resp = httpx.post(url, headers=headers, json=payload, timeout=120)
	resp.raise_for_status()
	data = resp.json()
	# HF often returns a list of dicts with 'generated_text'
	if isinstance(data, list) and len(data) > 0:
		item = data[0]
		if isinstance(item, dict) and "generated_text" in item:
			return item["generated_text"]
		if isinstance(item, str):
			return item
	# Fallback to string conversion
	return str(data)


