import pyroscope
from starlette.middleware.base import RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from src.middleware.base import ObservabilityMiddleware


class PyroscopeMiddleware(ObservabilityMiddleware):
    async def handle(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Use route template (e.g. /api/items/{item_id}) instead of raw path to avoid
        # high cardinality tags in Pyroscope.
        endpoint = self.get_route_path(request) or request.url.path
        with pyroscope.tag_wrapper({"endpoint": endpoint, "method": request.method}):
            return await call_next(request)
