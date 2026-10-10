FROM python:3.13-alpine AS builder

COPY --from=ghcr.io/astral-sh/uv:0.11.23 /uv /uvx /bin/

WORKDIR /orbit-board-api

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-install-project --no-dev


FROM python:3.13-alpine AS final

WORKDIR /orbit-board-api

RUN adduser -D -H -u 10001 orbit

COPY --from=builder --chown=orbit:orbit /orbit-board-api/.venv ./.venv
COPY --chown=orbit:orbit src/ ./src/
COPY --chown=orbit:orbit alembic/ ./alembic/
COPY --chown=orbit:orbit alembic.ini main.py ./

ENV PATH="/orbit-board-api/.venv/bin:$PATH"
ENV PYTHONPATH="/orbit-board-api/src"
ENV PYTHONUNBUFFERED=1
ENV FORWARDED_ALLOW_IPS="*"

USER orbit

EXPOSE 8000

CMD ["sh", "-c", "alembic upgrade head && exec python main.py"]
