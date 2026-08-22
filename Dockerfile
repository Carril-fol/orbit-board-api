FROM python:3.13-alpine AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /orbit-board-api

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-install-project --no-dev

COPY src/ ./src/
COPY alembic/ ./alembic/
COPY alembic.ini .
COPY main.py .


FROM python:3.13-alpine AS final

WORKDIR /orbit-board-api

RUN adduser -D -H -u 10001 orbit

COPY --from=builder --chown=orbit:orbit /orbit-board-api/.venv ./.venv
COPY --from=builder --chown=orbit:orbit /orbit-board-api/src ./src
COPY --from=builder --chown=orbit:orbit /orbit-board-api/alembic ./alembic
COPY --from=builder --chown=orbit:orbit /orbit-board-api/alembic.ini .
COPY --from=builder --chown=orbit:orbit /orbit-board-api/main.py .

ENV PATH="/orbit-board-api/.venv/bin:$PATH"
ENV PYTHONPATH="/orbit-board-api/src"
ENV PYTHONUNBUFFERED=1

USER orbit

EXPOSE 8000

CMD ["python", "main.py"]
