FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /src

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

COPY pyproject.toml /src/pyproject.toml
COPY uv.lock /src/uv.lock
ENV UV_PROJECT_ENVIRONMENT="/usr/local/"
RUN uv lock
RUN uv sync --locked

ENV PATH="/src/.venv/bin:$PATH"

COPY . /src
    
EXPOSE 8000