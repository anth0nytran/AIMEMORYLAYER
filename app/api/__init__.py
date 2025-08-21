from fastapi import APIRouter

# Aggregate router to collect all endpoint modules (added in later subtasks)
api_router = APIRouter()

# Include routers
from app.api.health import router as health_router  # noqa: E402
from app.api.chat import router as chat_router  # noqa: E402
from app.api.ingest import router as ingest_router  # noqa: E402

api_router.include_router(health_router)
api_router.include_router(chat_router)
api_router.include_router(ingest_router)


