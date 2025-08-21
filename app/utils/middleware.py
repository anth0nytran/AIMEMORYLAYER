import json
import time
import uuid
from collections import defaultdict
from typing import Callable, Dict

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from app.utils.settings import get_settings


class RequestIdAndLoggingMiddleware(BaseHTTPMiddleware):
	async def dispatch(self, request: Request, call_next: Callable) -> Response:
		request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
		start = time.perf_counter()
		response = await call_next(request)
		duration_ms = int((time.perf_counter() - start) * 1000)
		response.headers["x-request-id"] = request_id
		# Structured log to stdout
		log = {
			"ts": int(time.time()),
			"request_id": request_id,
			"method": request.method,
			"path": request.url.path,
			"status": response.status_code,
			"duration_ms": duration_ms,
		}
		print(json.dumps(log))
		return response


class SimpleRateLimitMiddleware(BaseHTTPMiddleware):
	def __init__(self, app):
		super().__init__(app)
		self._settings = get_settings()
		self._hits: Dict[str, Dict[int, int]] = defaultdict(lambda: defaultdict(int))

	async def dispatch(self, request: Request, call_next: Callable) -> Response:
		# Very simple IP-based RPM limiter for MVP
		ip = request.client.host if request.client else "unknown"
		now_minute = int(time.time() // 60)
		self._hits[ip][now_minute] += 1
		if self._hits[ip][now_minute] > self._settings.rate_limit_rpm:
			return Response("Rate limit exceeded", status_code=429)
		return await call_next(request)


