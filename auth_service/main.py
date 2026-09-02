from fastapi import FastAPI
from fastapi.responses import JSONResponse
from auth_service.auth_routes import router
from sqlalchemy.exc import OperationalError,IntegrityError,TimeoutError
from logger import log
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI()

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
