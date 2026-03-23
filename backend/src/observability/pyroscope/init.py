import pyroscope

from src.env import APP_NAME, PYROSCOPE_HOST, PYROSCOPE_PORT


def init_pyroscope(
    application_name: str = APP_NAME,
    host: str = PYROSCOPE_HOST,
    port: int = PYROSCOPE_PORT,
    secure: bool = False,
):
    # Per-endpoint CPU profiling via pyroscope.tag_wrapper is not supported in async Python:
    # tag_wrapper uses thread-local storage, so tags leak across concurrent coroutines on the
    # same OS thread. Per-trace profiles are linked via PyroscopeSpanProcessor instead.
    # https://github.com/grafana/pyroscope-rs/issues/132
    scheme = "https" if secure else "http"
    pyroscope.configure(
        application_name=application_name,
        server_address=f"{scheme}://{host}:{port}",
        sample_rate=100,
        oncpu=True,
        gil_only=True,
    )
