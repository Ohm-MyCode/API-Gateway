import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from redis.asyncio import Redis

from gateway.main import app


@pytest.fixture(autouse=True)
def client():
    with TestClient(app) as client:
        yield client

@pytest_asyncio.fixture(autouse=True)
async def clear_redis():
    redis = Redis(host="localhost", port=6379)
    await redis.flushdb()
    yield
    await redis.aclose()