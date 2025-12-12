FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential curl && \
    rm -rf /var/lib/apt/lists/* && \
    pip install --no-cache-dir uv

COPY pyproject.toml uv.lock ./
RUN uv export --no-dev --no-hashes -o requirements.txt && \
    uv pip install -r requirements.txt --system

COPY src/ /app/src/
COPY gunicorn.conf.py /app/gunicorn.conf.py

EXPOSE 8000

CMD ["gunicorn", "src.main:app", "-c", "gunicorn.conf.py"]
