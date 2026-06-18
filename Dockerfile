FROM python:3.12-slim AS builder

WORKDIR /app
COPY . .

RUN pip install --no-cache-dir build && \
    pip install --no-cache-dir fastapi uvicorn && \
    pip install -e .

FROM python:3.12-slim

RUN groupadd -r isre && useradd -r -g isre -d /app isre

WORKDIR /app
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /app/isre /app/isre
COPY --from=builder /app/pyproject.toml /app/

USER isre

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "isre.api.server:app", "--host", "0.0.0.0", "--port", "8000"]
