FROM python:3.13-alpine AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /project-board-api

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-install-project --no-dev

COPY src/ ./src/
COPY alembic/ ./alembic/
COPY alembic.ini .
COPY main.py .


FROM python:3.13-alpine AS final

WORKDIR /project-board-api

COPY --from=builder /project-board-api/.venv ./.venv
COPY --from=builder /project-board-api/src ./src
COPY --from=builder /project-board-api/alembic ./alembic
COPY --from=builder /project-board-api/alembic.ini .
COPY --from=builder /project-board-api/main.py .

ENV PATH="/project-board-api/.venv/bin:$PATH"
ENV PYTHONPATH="/project-board-api/src"

CMD ["python", "main.py"]