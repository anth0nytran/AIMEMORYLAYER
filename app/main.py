from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.utils.settings import get_settings
from app.utils.middleware import RequestIdAndLoggingMiddleware, SimpleRateLimitMiddleware

try:
	# Import the aggregated API router if available
	from app.api import api_router  # type: ignore
except Exception:
	api_router = None  # Fallback if not yet created


settings = get_settings()

app = FastAPI(title=settings.app_name, version="0.1.0")

# CORS per FastAPI docs
# https://github.com/tiangolo/fastapi/blob/master/docs/en/docs/tutorial/cors.md#_snippet_0
app.add_middleware(
	CORSMiddleware,
	allow_origins=settings.cors_origins,
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)

# Basic request ID + JSON logs, then simple RPM limiter
app.add_middleware(RequestIdAndLoggingMiddleware)
app.add_middleware(SimpleRateLimitMiddleware)

if api_router is not None:
	app.include_router(api_router, prefix="/api")


