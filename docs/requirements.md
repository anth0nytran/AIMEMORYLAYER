## AI Memory Layer MVP — Requirements

### Overview
Build a resume-ready, deployed chatbot with per-user memory using FastAPI, Hugging Face LLMs, Pinecone for memory, and a Gradio UI. Ship as a fully Dockerized app on a low-cost AWS EC2 instance with CI/CD via GitHub Actions.

---

### Definition of Done
- Deployed public demo (URL) serving Gradio chat UI.
- Each user has isolated memory (Pinecone namespace per `user_id`; metadata filter as fallback).
- Backend: FastAPI API connected to Hugging Face LLM + embeddings + Pinecone.
- Retrieval-augmented chat: store memory → retrieve relevant context → generate response.
- Dockerized services; reproducible local dev (Docker Compose).
- CI/CD: On push to `main`, build Docker image and deploy to AWS EC2.
- Repo: Clear README, architecture diagram, environment setup, run/deploy steps, sample requests, tests (smoke/unit).
- Observability: health check, request logging, basic metrics.
- Cost-aware: runs on a single small EC2 instance.
 - Version control: GitHub-first workflow with branches + PRs; every change committed and pushed; tagged releases for milestones; rollback via tags.

---

### In Scope
- Gradio chat frontend (simple, session-based).
- FastAPI backend: chat endpoint, memory store/retrieve, health.
- Embeddings + vector store (Pinecone).
- Generation via Hugging Face (Inference API or local small model).
- Minimal user identification (cookie or header-based `user_id`).
- Docker, AWS EC2 deploy, GitHub Actions pipeline.

### Out of Scope (MVP)
- Full auth (OAuth), billing, role-based access control.
- Multi-region HA, horizontal autoscaling.
- Complex prompt engineering/agents/tools.
- Advanced analytics dashboard.

---

### Functional Requirements
- User Identity
  - Assign or accept a `user_id` per session (cookie/local storage token or query param).
  - No PII collected; anonymous IDs are acceptable.

- Chat Flow
  - Input: user message + `user_id`.
  - Pipeline:
    1) Embed message.
    2) Upsert message to Pinecone as memory.
    3) Retrieve top-k relevant memories for `user_id`.
    4) Construct prompt with system instructions + retrieved context + latest message.
    5) Call LLM for response.
    6) Return response; stream if feasible.
  - Store assistant responses optionally for improved future retrieval.

- Memory
  - Pinecone index created and configured.
  - Isolation by user via namespace or metadata filter (prefer namespace).
  - Configurable `top_k`, score threshold, and decay/recency bias (simple timestamp re-ranking if needed).

- Models (Decisions)
  - Embeddings: `sentence-transformers/all-MiniLM-L6-v2` (HF Inference API by default; local optional).
  - LLM: `mistralai/Mistral-7B-Instruct-v0.2` via Hugging Face Inference API; acceptable alternatives: Llama 3 8B instruction-tuned.
  - Model selection is configurable via env vars.

- Gradio UI
  - Single chat window with history for the session.
  - Lightweight header: project name, link to repo.
  - Option to set/edit `user_id` for testing.

- Admin/Operations
  - Health endpoint: `/api/health` returns status of FastAPI, Pinecone, and model connectivity.
  - Basic rate limiting (simple in-memory or token bucket).

---

### Non-Functional Requirements
- Performance: P95 end-to-end latency ≤ 4s (API-based LLM), ≤ 8s (local).
- Availability: Single-instance; graceful restarts.
- Cost: Fits on t3.small/t3.micro; uses free/low-tier API options.
- Security: API keys via env vars; CORS restricted to demo domain.
- Observability: Structured logs, request IDs, minimal metrics (request count, latency).

---

### Architecture
- Components
  - Gradio (frontend)
  - FastAPI (backend)
  - Embeddings model (HF Inference API or local)
  - Pinecone (vector DB)
  - LLM (HF Inference API or local)
  - AWS EC2 host + Docker

- Sequence
  - Gradio → FastAPI `/api/chat` → embed → Pinecone query → construct prompt → LLM → response → return → display in Gradio.

- Diagram content (nodes and edges)
  - Nodes: User, Gradio, FastAPI, Embeddings, Pinecone, LLM (HF), AWS EC2.
  - Edges: User→Gradio; Gradio→FastAPI; FastAPI→Embeddings; FastAPI↔Pinecone; FastAPI→LLM; LLM→FastAPI; FastAPI→Gradio.

- Data Model (Pinecone vector)
  - id: string (e.g., `user_id:timestamp:uuid`)
  - vector: float[] embedding
  - metadata:
    - user_id: string
    - role: "user" | "assistant"
    - text: string
    - ts: ISO timestamp
    - tags: optional list
    - conversation_id: optional

---

### API Design
- POST `/api/chat`
  - Request example:
  {
    "user_id": "anon_123",
    "message": "How did we define the scope?",
    "top_k": 5,
    "metadata": { "conversation_id": "default" }
  }
  - Response example:
  {
    "response": "Here's what we scoped...",
    "context": [
      { "text": "Past message...", "score": 0.82, "ts": "..." }
    ],
    "usage": { "prompt_tokens": 0, "completion_tokens": 0, "model": "mistral-7b" },
    "latency_ms": 1234
  }

- POST `/api/ingest` (optional for bootstrapping memory)
  - Request example:
  {
    "user_id": "anon_123",
    "items": [
      { "text": "Seed memory 1", "role": "user" },
      { "text": "Seed memory 2", "role": "assistant" }
    ]
  }
  - Response: { "upserted": 2 }

- GET `/api/health`
  - Response: { "status": "ok", "pinecone": "ok", "hf": "ok", "version": "x.y.z" }

- CORS
  - Allowlist Gradio origin; deny others by default.

---

### Configuration and Secrets
- Required env vars
  - `HF_TOKEN` (if using Hugging Face Inference API)
  - `HF_LLM_MODEL` (default: `mistralai/Mistral-7B-Instruct-v0.2`)
  - `HF_EMBEDDING_MODEL` (default: `sentence-transformers/all-MiniLM-L6-v2`)
  - `PINECONE_API_KEY`
  - `PINECONE_INDEX`
  - `PINECONE_REGION`
  - `TOP_K` (default 5)
  - `CORS_ORIGINS` (comma-separated)
  - `PORT` (default 8000)
  - `LOG_LEVEL` (info/debug)

- `.env.example`
  HF_TOKEN=
  HF_LLM_MODEL=mistralai/Mistral-7B-Instruct-v0.2
  HF_EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
  PINECONE_API_KEY=
  PINECONE_INDEX=ai-memory-mvp
  PINECONE_REGION=us-east-1
  TOP_K=5
  CORS_ORIGINS=http://localhost:7860
  PORT=8000
  LOG_LEVEL=info

---

### Deployment
- Docker
  - Single container running FastAPI and Gradio, or two containers behind a simple reverse proxy; MVP can colocate to simplify.
- AWS EC2
  - Ubuntu LTS on t3.small/t3.micro.
  - Security group: allow 80/443 and SSH (22).
  - Optional: Nginx reverse proxy and Certbot for HTTPS.
- Docker Compose (local)
  services:
    api:
      build: .
      env_file: .env
      ports: ["8000:8000"]

---

### CI/CD (GitHub Actions)
- Triggers: push to `main`, PRs for lint/test.
- Jobs:
  - Lint + test.
  - Build Docker image.
  - Push to registry (Docker Hub or ECR).
  - Deploy:
    - Option A: SSH to EC2, `docker pull`, `docker run --restart=always`.
    - Option B: Self-hosted runner on EC2 to pull and restart container.

- Minimal workflow skeleton (high-level)
  - Checkout, setup Python
  - Install deps and run tests
  - Build and push Docker image
  - SSH into EC2 and restart container

---

### Version Control & Workflow
- GitHub as source of truth; all work occurs via branches and PRs.
- Protect `main`: require PR reviews and passing checks before merge.
- After each meaningful change:
  - Commit with conventional message (e.g., feat:, fix:, docs:).
  - Push branch to GitHub and open PR.
  - Merge via squash or rebase after checks pass.
- Tag milestones/releases (e.g., `v0.1.0`) for rollback.
- Keep `.cursor/mcp.json` and other secrets out of Git via `.gitignore`.

---

### Testing
- Unit tests for:
  - Embedding + upsert.
  - Retrieval query and top_k logic.
  - Prompt assembly.
- Integration tests:
  - `/api/chat` with mocked HF/Pinecone.
- Smoke test workflow job against deployed URL.
- Optional load test with `k6` for 5–10 RPS.

---

### Observability
- Structured JSON logs with request_id and user_id (no PII).
- Health endpoint checks downstreams.
- Basic metrics: request count, latency histogram (Prometheus-compatible if time permits).

---

### Security and Compliance
- Do not log message content at debug level in prod.
- Secrets via env or SSM Parameter Store (later).
- CORS allowlist; CSRF not needed for pure API POSTs with tokens.
- HTTPS via Nginx/Certbot recommended.

---

### Performance Targets
- P95 latency ≤ 4s with API-based LLM; ≤ 8s local model.
- Memory retrieval: ≤ 150ms for top_k=5.
- Cold start: ≤ 30s on EC2 after deploy.

---

### Risks & Mitigations
- Model latency/cost: Prefer HF Inference API initially; cache results where safe.
- Pinecone cost/limits: Use small pod or serverless tier; prune old memories.
- EC2 resource limits: Start small; monitor; scale instance if needed.

---

### Milestones and Acceptance Criteria
- Phase 1 — Local Prototype
  - Chat works locally; Pinecone stores/retrieves per user; LLM responds.
- Phase 2 — Demo UI
  - Gradio linked to FastAPI; chat history visible; multiple users via `user_id`.
- Phase 3 — Deployment
  - Public URL live; logs visible; health returns ok.
- Phase 4 — CI/CD + Polish
  - Main push auto-deploys; README + diagram; demo link in README.

---

### Repo Structure (Proposed)
/ (root)
  README.md
  requirements.txt
  requirements-dev.txt
  .env.example
  docker/Dockerfile
  docker/docker-compose.yml
  infra/ (optional scripts, nginx)
  app/
    main.py              # FastAPI app
    api/                 # routes
    services/            # embeddings, llm, pinecone
    models/              # pydantic schemas
    utils/               # logging, ids
    gradio_app.py
    prompts/
    tests/
  .github/workflows/ci-cd.yml
  docs/architecture.png

---

### Documentation Deliverables
- README: quickstart, env setup, run locally, deploy, endpoints.
- Architecture Diagram: User → Gradio → FastAPI → Pinecone → Hugging Face → AWS.
- Live demo link.

---

### License
- MIT License (simple and permissive).


