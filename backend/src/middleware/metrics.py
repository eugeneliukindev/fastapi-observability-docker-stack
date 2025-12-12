import time
from typing import TypeAlias

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Match
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR
from starlette.types import ASGIApp

from src.__version__ import VERSION
from src.config import EXCLUDED_PATHS_GRAFANA

from src.observability.prometheus.constants import (
    EXCEPTIONS,
    INFO,
    REQUESTS,
    REQUESTS_IN_PROGRESS,
    REQUESTS_PROCESSING_TIME,
    RESPONSES,
)

RequestPath: TypeAlias = str
RouteTemplatedPath: TypeAlias = str
IsHandledPath: TypeAlias = bool


class MetricsMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, version: str = VERSION) -> None:
        super().__init__(app)
        INFO.labels(version=version).set(1)

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        method = request.method
        if request.url.path in EXCLUDED_PATHS_GRAFANA:
            return await call_next(request)

        path, is_handled_path = self._get_path(request)
        if not is_handled_path:
            return await call_next(request)

        REQUESTS.labels(method=method, path=path).inc()
        REQUESTS_IN_PROGRESS.labels(method=method, path=path).inc()
        before_time = time.perf_counter()
        try:
            response = await call_next(request)
        except BaseException as e:
            status_code = HTTP_500_INTERNAL_SERVER_ERROR
            EXCEPTIONS.labels(method=method, path=path, exception_type=type(e).__name__).inc()
            raise e from None
        else:
            status_code = response.status_code
            REQUESTS_PROCESSING_TIME.labels(method=method, path=path).observe(time.perf_counter() - before_time)
        finally:
            RESPONSES.labels(method=method, path=path, status_code=status_code).inc()
            REQUESTS_IN_PROGRESS.labels(method=method, path=path).dec()

        return response

    @staticmethod
    def _get_path(request: Request) -> tuple[RouteTemplatedPath, IsHandledPath]:
        for route in request.app.routes:
            match, _child_scope = route.matches(request.scope)
            if match == Match.FULL:
                return route.path, True
        return "", False
