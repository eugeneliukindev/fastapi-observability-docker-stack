from typing import Final

EXCLUDED_PATHS_GRAFANA: Final[frozenset[str]] = frozenset({"/metrics", "/metrics/", "/health", "/health/"})
