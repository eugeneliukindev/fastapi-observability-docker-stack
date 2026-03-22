from abc import ABC, abstractmethod

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Match
from starlette.types import ASGIApp

from src.config import EXCLUDED_PATHS_GRAFANA


class ObservabilityMiddleware(BaseHTTPMiddleware, ABC):
    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)
        self._route_cache: dict[str, str | None] = {}

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if request.url.path in EXCLUDED_PATHS_GRAFANA:
            return await call_next(request)
        return await self.handle(request, call_next)

    def get_route_path(self, request: Request) -> str | None:
        """Returns the route template path (e.g. /api/items/{item_id}) for the request,
        or None if no route matches. Results are cached by raw path to avoid iterating
        all routes on every request."""
        raw_path = request.url.path
        if raw_path in self._route_cache:
            return self._route_cache[raw_path]

        for route in request.app.routes:
            match, _ = route.matches(request.scope)
            if match == Match.FULL:
                self._route_cache[raw_path] = route.path
                return route.path

        self._route_cache[raw_path] = None
        return None

    @abstractmethod
    async def handle(self, request: Request, call_next: RequestResponseEndpoint) -> Response: ...
