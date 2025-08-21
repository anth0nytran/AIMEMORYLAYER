from app.services.pinecone_client import rerank_by_recency_and_score


class DummyMatch:
	def __init__(self, score, text, role, ts):
		self.score = score
		self.metadata = {"text": text, "role": role, "ts": ts}


def test_rerank_prefers_recent_when_scores_equal():
	old = DummyMatch(0.8, "old msg", "user", "2020-01-01T00:00:00Z")
	new = DummyMatch(0.8, "new msg", "user", "2100-01-01T00:00:00Z")
	ordered = rerank_by_recency_and_score([old, new])
	assert ordered[0].metadata["text"] == "new msg"


