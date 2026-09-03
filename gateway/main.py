from fastapi import FastAPI, Request, HTTPException
from contextlib import asynccontextmanager
import httpx
from gateway.config import settings
from fastapi.responses import Response
from redis.asyncio import Redis
from gateway.logger import log
from gateway.middlewares import auth_middleware , logging_middleware, rate_limiting_middleware
from gateway.config import SERVICES
from time import perf_counter
from prometheus_fastapi_instrumentator import Instrumentator

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.http_client = httpx.AsyncClient(timeout=httpx.Timeout(30.0))
    redis_client = Redis(host=settings.redis_host,port=settings.redis_port,decode_responses=True,
                         socket_connect_timeout=0.5,socket_timeout=0.5)
    script = settings.lua_script()
    app.state.token_bucket_script = redis_client.register_script(script)
    yield
    await app.state.http_client.aclose()
    await redis_client.aclose()

app = FastAPI(lifespan=lifespan)

Instrumentator().instrument(app).expose(app)

app.middleware("http")(logging_middleware.req_logging)
app.middleware("http")(auth_middleware.auth_middleware)
app.middleware("http")(rate_limiting_middleware.rate_limiter)


@app.get("/{shortcode}")
async def resolve_shortcode(shortcode: str, request: Request):
    response = await request.app.state.http_client.get(
        f"http://url-service:8000/{shortcode}"
    )
    return Response(
        content=response.content,
        status_code=response.status_code,
        headers=dict(response.headers),
    )

@app.api_route("/{service}/{path:path}",methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def proxy(service: str,path: str,request: Request):
    baseurl = SERVICES.get(service)
    if not baseurl:
        log.critical("unkown_endpoint", url_path=request.url.path)
        raise HTTPException(status_code=404,detail="Unknown service")
    body = await request.body()
    target_url = f"{baseurl}/{path}"
    request_id = getattr(request.state,"request_id")

    if service == "auth":
        headers = dict(request.headers)
        headers.pop("host", None)
        headers["x-request-id"]=request_id

    else:
        headers={}
        user_id= getattr(request.state,"userid",None)
        if user_id is not None:
            headers["x-user-id"] = user_id
        else :
            raise HTTPException(status_code = 500, detail = "Try Logging In Again or Creating New Account")

        content_type = request.headers.get("content-type")
        if content_type:
            headers["content-type"] = content_type
        headers["x-request-id"]=request_id

    service_start= perf_counter()
    try:
        response = await request.app.state.http_client.request(method=request.method,url=target_url,
                                        headers=headers,params=request.query_params,content=body,)
        log.info("upstream_response", service=service, status_code=response.status_code,
          upstream_duration_ms=round((perf_counter()-service_start)*1000, 2))
    except httpx.RequestError as e:
        log.error("service_unreachable", service=service, target_url=target_url, error=str(e))
        raise HTTPException(status_code=502, detail="service unavailable")

    return Response(content=response.content,status_code=response.status_code,headers=dict(response.headers),)