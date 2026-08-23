FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN pip install uv

RUN uv sync --frozen --no-dev

COPY url_service ./url_service

RUN chmod +x /app/url_service/start.sh

CMD ["/app/url_service/start.sh"]