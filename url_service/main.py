from fastapi import FastAPI
from contextlib import asynccontextmanager
from url_service.url_routes import router
from fastapi.responses import JSONResponse
from sqlalchemy.exc import OperationalError,IntegrityError,TimeoutError
from url_service.logger import log
from prometheus_fastapi_instrumentator import Instrumentator
from redis.asyncio import Redis
from url_service.config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    redis_client = Redis(host=settings.redis_host,port=settings.redis_port,decode_responses=True,)
    app.state.redis_client = redis_client
    yield
    await redis_client.aclose()

app = FastAPI(lifespan=lifespan)

Instrumentator().instrument(app).expose(app) 

app.include_router(router)

@app.exception_handler(OperationalError)
async def operation_error(request, exc:OperationalError):
    log.critical("Database Unreachable",path=request.url.path,method=request.method,error=str(exc),)
    return JSONResponse(status_code=503, content={"detail": "Service temporarily unavailable"})

@app.exception_handler(TimeoutError)
async def timeout(request,exc:TimeoutError):
    log.warning("Connection TimeOut", path=request.url.path, method = request.method, error=str(exc),)
    return JSONResponse(status_code=503, content={"detail": "Service temporarily unavailable"})

@app.exception_handler(IntegrityError)
async def integrity_error(request,exc:IntegrityError):
    log.info("Integrity Error",path=request.url.path,method=request.method,error=str(exc),)
    return JSONResponse(status_code=409, content={"detail": "Resource Already Exists"})