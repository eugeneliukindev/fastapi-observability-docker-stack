import time
import uuid
from typing import Final

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from src.config import EXCLUDED_PATHS_GRAFANA
from src.logger import log, request_id_ctx_var

REQUEST_ID_HEADER: Final[str] = "X-Request-Id"
MS_IN_SECOND: Final[int] = 1000

ACCESS_LOG_MESSAGE_FORMAT: Final[str] = "HTTP | method=%s | url=%s | status=%d | dur=%dms | ua=%s | size=%d"


class RequestAccessMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if request.url.path in EXCLUDED_PATHS_GRAFANA:
            return await call_next(request)

        request_id = request.headers.get(REQUEST_ID_HEADER) or uuid.uuid4().hex[:10]
        request_id_ctx_var.set(request_id)

        method = request.method
        path = request.url.path
        query = request.url.query
        full_url = f"{path}?{query}" if query else path
        user_agent = request.headers.get("user-agent", "-")

        start_time = time.perf_counter()
        response = await call_next(request)
        duration_ms = int((time.perf_counter() - start_time) * MS_IN_SECOND)

        response.headers[REQUEST_ID_HEADER] = request_id

        log.info(
            ACCESS_LOG_MESSAGE_FORMAT,
            method,
            full_url,
            response.status_code,
            duration_ms,
            user_agent,
            int(response.headers.get("content-length", 0)),
        )
        return response
