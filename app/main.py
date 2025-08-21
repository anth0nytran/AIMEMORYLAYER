from fastapi import FastAPI

try:
	# Import the aggregated API router if available
	from app.api import api_router  # type: ignore
except Exception:
	api_router = None  # Fallback if not yet created


app = FastAPI(title="AI Memory Layer MVP", version="0.1.0")

if api_router is not None:
	app.include_router(api_router, prefix="/api")


