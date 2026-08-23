FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN pip install uv

RUN uv sync --frozen --no-dev

COPY auth_service ./auth_service

RUN chmod +x /app/auth_service/start.sh

CMD ["/app/auth_service/start.sh"]