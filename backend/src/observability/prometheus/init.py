from __future__ import annotations

from typing import TYPE_CHECKING

from prometheus_client import CollectorRegistry, make_asgi_app, multiprocess

if TYPE_CHECKING:
    from fastapi import FastAPI


def init_prometheus(app: FastAPI) -> None:
    def make_metrics_app():
        registry = CollectorRegistry()
        multiprocess.MultiProcessCollector(registry)
        return make_asgi_app(registry=registry)

    app.mount(path="/metrics", app=make_metrics_app(), name="metrics")
