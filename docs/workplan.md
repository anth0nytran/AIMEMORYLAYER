## AI Memory Layer MVP — Workplan (Tasks & Subtasks)

Status legend: [ ] = todo, [x] = done, [~] = in progress
Last updated: 2025-08-21

---

## Main Task 1 — Discovery, Scope, and Documentation
- [x] a) Finalize MVP scope and success criteria (Definition of Done)
- [x] b) Establish docs structure (`/docs` with separate workplan and requirements)
- [x] c) Draft initial `requirements.md` with full content
- [x] d) Define architecture diagram content (nodes and edges)
- [x] e) Choose final models (LLM + embeddings) and fallbacks
- [x] f) Define per-user memory strategy (namespace vs metadata) — decision: namespace per `user_id`
- [x] g) Capture non-functional targets (perf, cost, security) in requirements

## Main Task 2 — Backend: FastAPI Scaffolding
- [x] a) Initialize FastAPI app structure (`app/main.py`, `app/api`, `app/models`, `app/services`)
- [x] b) Add Pydantic schemas (`ChatRequest`, `ChatResponse`, `HealthResponse`)
- [x] c) Add routes: `/api/chat`, `/api/ingest`, `/api/health`
- [x] d) Add settings loader (env vars, `.env.example`)
- [x] e) Add CORS config and basic rate limiting
- [x] f) Add request/response logging with request_id and user_id

## Main Task 3 — Memory Layer: Pinecone Integration
- [x] a) Initialize Pinecone client and index config
- [x] b) Implement upsert function with `user_id` isolation (namespace/metadata)
- [x] c) Implement query function with `top_k`, score threshold
- [ ] d) Add simple recency bias (timestamp re-ranking)
- [ ] e) Unit tests: upsert and retrieval logic (mocked Pinecone)

## Main Task 4 — Embeddings + LLM (Hugging Face)
- [x] a) Implement embeddings service (HF Inference API or local)
- [x] b) Implement LLM generation service (Mistral 7B / Llama 3 8B via HF)
- [x] c) Prompt assembly with retrieved context + system instructions
- [ ] d) Optional streaming support for responses
- [ ] e) Unit tests: prompt assembly and service adapters (mock HF)

## Main Task 5 — Chat Flow Integration
- [~] a) Wire pipeline: message → embed → upsert → retrieve → prompt → LLM
- [ ] b) Include retrieved context in response payload for visibility
- [ ] c) Optionally store assistant responses for future retrieval
- [ ] d) Integration test: `/api/chat` end-to-end with mocks

## Main Task 6 — Frontend (Gradio MVP)
- [ ] a) Create `app/gradio_app.py` with a simple chat UI
- [ ] b) Add ability to set `user_id` in UI for testing multi-user
- [ ] c) Connect Gradio to FastAPI `/api/chat`
- [ ] d) Show chat history and relevant retrieved context
- [ ] e) Local demo verification

## Main Task 7 — Local Dev + Testing
- [x] a) Add `requirements.txt` and `requirements-dev.txt`
- [ ] b) Configure pytest with unit and integration tests
- [ ] c) Add Makefile or simple scripts for run/test/lint (optional)
- [ ] d) Smoke test script for `/api/health` and `/api/chat`

## Main Task 8 — Containerization (Docker)
- [ ] a) Create `docker/Dockerfile` (multi-stage if needed)
- [ ] b) Create `docker/docker-compose.yml` for local reproducibility
- [ ] c) Ensure env variables and ports are correctly wired
- [ ] d) Verify container runs locally (FastAPI + Gradio)

## Main Task 9 — Deployment (AWS EC2)
- [ ] a) Provision t3.micro/t3.small Ubuntu EC2 with security group (80/443/22)
- [ ] b) Install Docker and set up `.env` on instance
- [ ] c) Deploy container and expose (80 → 8000)
- [ ] d) Optional: Nginx reverse proxy + Certbot for HTTPS
- [ ] e) Validate public URL and health

## Main Task 10 — CI/CD (GitHub Actions)
- [ ] a) Workflow: lint/test → build Docker → push to registry
- [ ] b) Deploy via SSH action or self-hosted runner
- [ ] c) Set GitHub Secrets (DOCKERHUB_USER/TOKEN, EC2 creds)
- [ ] d) Auto-redeploy on push to `main`
- [ ] e) Add smoke test step against live URL

## Main Task 11 — Observability, Security, and Performance
- [ ] a) Health checks for Pinecone and HF connectivity
- [ ] b) Structured logs (JSON) with request_id; avoid PII
- [ ] c) Basic metrics (request count, latency)
- [ ] d) CORS allowlist; minimal rate limiting
- [ ] e) Performance targets documented and spot-checked

## Main Task 12 — Documentation, Diagram, and Demo Polish
- [ ] a) Expand `docs/requirements.md` if needed
- [ ] b) Add architecture diagram (`docs/architecture.png`)
- [ ] c) Write `README.md` (quickstart, run, deploy, links)
- [ ] d) Add live demo link in README
- [ ] e) Final repo review for resume-readiness

---

## Main Task 13 — Version Control & Repo Management
- [x] a) Add GitHub-first workflow to requirements and DoD
- [x] b) Add `.gitignore` to exclude secrets and `.cursor/mcp.json`
- [x] c) Initialize local Git repository and first commit
- [x] d) Create new GitHub repo, set `origin`, push `main`
- [ ] e) Configure branch protection and required checks
- [x] f) Follow PR-based workflow with conventional commits and tags
- [x] g) Commit and push after each meaningful change

---

### Decisions captured
- Embeddings model: `sentence-transformers/all-MiniLM-L6-v2` (HF Inference API default; local optional)
- LLM: `mistralai/Mistral-7B-Instruct-v0.2` via HF Inference API (fallback allowed)
- Memory isolation: Pinecone namespace per `user_id` (metadata filter as backup)
- Deployment target: Single EC2 (t3.micro/small) with Docker; optional Nginx/Certbot


