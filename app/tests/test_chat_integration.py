import json
from fastapi.testclient import TestClient
from app.main import app


def test_chat_endpoint_smoke(monkeypatch):
	# Monkeypatch embeddings and pinecone for deterministic response
	from app import services

	def fake_embed_text(text: str):
		return [0.1, 0.2, 0.3, 0.4]

	class FakeMatch:
		def __init__(self, score, text, role):
			self.score = score
			self.metadata = {"text": text, "role": role, "ts": "2100-01-01T00:00:00Z"}

	class FakeResult:
		def __init__(self):
			self.matches = [FakeMatch(0.9, "hello memory", "user")]

	def fake_query_top_k(**kwargs):
		return FakeResult()

	def fake_generate_response(prompt: str, **_):
		return "This is a test response"

	monkeypatch.setattr("app.services.embeddings.embed_text", fake_embed_text)
	monkeypatch.setattr("app.services.pinecone_client.query_top_k", lambda **kw: fake_query_top_k())
	monkeypatch.setattr("app.services.llm.generate_response", fake_generate_response)
	# prevent upserts
	monkeypatch.setattr("app.services.pinecone_client.upsert_vectors", lambda **kw: None)

	client = TestClient(app)
	r = client.post("/api/chat", json={"user_id": "u1", "message": "hi", "top_k": 3})
	assert r.status_code == 200, r.text
	data = r.json()
	assert "response" in data and isinstance(data["response"], str)
	assert "context" in data and isinstance(data["context"], list)


