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
        """Return the route template path (e.g. /api/items/{item_id}) for the request,
        or None if no route matches.

        Results are cached in-process by raw path to avoid iterating all routes on
        every request. The cache is unbounded — in practice it stays small because the
        number of distinct raw paths is bounded by the number of routes × distinct
        path-param values seen. For high-cardinality path params (e.g. UUIDs) the cache
        can grow large; in that case replace the dict with a shared Redis hashmap so all
        Gunicorn workers share a single warmed cache instead of each building their own:

            async def get_route_path_redis(self, request: Request) -> str | None:
                raw_path = request.url.path

                # Redis HGET/HSET stores all routes under one key — avoids per-key TTL
                # overhead and keeps the cache queryable as a single hash for inspection.
                cached = await redis.hget("route_cache", raw_path)
                if cached is not None:
                    return cached or None  # empty string is stored for unmatched paths

                for route in request.app.routes:
                    match, _ = route.matches(request.scope)
                    if match == Match.FULL:
                        await redis.hset("route_cache", raw_path, route.path)
                        return route.path

                await redis.hset("route_cache", raw_path, "")
                return None
        """
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
