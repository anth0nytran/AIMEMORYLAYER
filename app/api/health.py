from fastapi import APIRouter

from app.models.schemas import HealthResponse


router = APIRouter(prefix="/health", tags=["health"])


@router.get("", response_model=HealthResponse)
def get_health() -> HealthResponse:
	# Placeholder health; downstream checks wired in later subtasks
	return HealthResponse(status="ok", version="0.1.0")


