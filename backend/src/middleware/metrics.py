import time

from starlette.middleware.base import RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR
from starlette.types import ASGIApp

from src.__version__ import VERSION
from src.middleware.base import ObservabilityMiddleware
from src.observability.prometheus.constants import (
    EXCEPTIONS,
    INFO,
    REQUESTS,
    REQUESTS_IN_PROGRESS,
    REQUESTS_PROCESSING_TIME,
    RESPONSES,
)


class MetricsMiddleware(ObservabilityMiddleware):
    def __init__(self, app: ASGIApp, version: str = VERSION) -> None:
        super().__init__(app)
        INFO.labels(version=version).set(1)

    async def handle(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        method = request.method
        path = self.get_route_path(request)
        if path is None:
            return await call_next(request)

        REQUESTS.labels(method=method, path=path).inc()
        REQUESTS_IN_PROGRESS.labels(method=method, path=path).inc()
        before_time = time.perf_counter()
        status_code = HTTP_500_INTERNAL_SERVER_ERROR
        try:
            response = await call_next(request)
        except BaseException as e:
            status_code = HTTP_500_INTERNAL_SERVER_ERROR
            EXCEPTIONS.labels(method=method, path=path, exception_type=type(e).__name__).inc()
            raise
        else:
            status_code = response.status_code
            # Exemplars are not supported with prometheus_multiproc mode — observe() accepts
            # an exemplar kwarg but the multiprocess value collector silently drops them.
            REQUESTS_PROCESSING_TIME.labels(method=method, path=path).observe(time.perf_counter() - before_time)
        finally:
            RESPONSES.labels(method=method, path=path, status_code=status_code).inc()
            REQUESTS_IN_PROGRESS.labels(method=method, path=path).dec()

        return response
