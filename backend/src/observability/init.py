from __future__ import annotations

from typing import TYPE_CHECKING

from .opentelemetry import init_otlp
from .prometheus import init_prometheus
from .pyroscope import init_pyroscope

if TYPE_CHECKING:
    from fastapi import FastAPI


def init_observability(app: FastAPI):
    init_prometheus(app=app)
    init_pyroscope()
    init_otlp(app=app)
