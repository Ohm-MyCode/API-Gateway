from fastapi import FastAPI, Request, HTTPException
from contextlib import asynccontextmanager
import httpx
from .config import settings
import jwt
from fastapi.responses import JSONResponse, Response


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.http_client = httpx.AsyncClient()
    yield
    await app.state.http_client.aclose()

app = FastAPI(lifespan=lifespan)

SERVICES = {
    "auth": "http://localhost:8001",
    "url": "http://localhost:8002",
}

PUBLIC_ROUTES = {
    "/auth/login",
    "/auth/signup",
    "/auth/refresh",
    "/auth/logout",
    "/auth/logout-all"
}

@app.middleware("http")
async def auth_middleware(request, call_next):

    if request.url.path in PUBLIC_ROUTES:
        return await call_next(request)

    if request.method == "GET":
        parts = request.url.path.strip("/").split("/")
        if len(parts) == 1 and parts[0] not in SERVICES:
            return await call_next(request)
        
    auth = request.headers.get("Authorization")
    if not auth:
        return JSONResponse(
            {"detail": "Unauthorized"},
            status_code=401,
        )
    try:
        scheme, token = auth.split()
        payload = jwt.decode(token,settings.PUBLIC_KEY , algorithms=[settings.JWT_ALGORITHM])
        request.state.userid = payload["sub"]
        
    except jwt.PyJWTError:
        return JSONResponse({"details":"Unauthorized, try logging in again"},status_code=401)
    return await call_next(request)

@app.get("/{shortcode}")
async def resolve_shortcode(shortcode: str, request: Request):
    response = await request.app.state.http_client.get(
        f"http://localhost:8002/{shortcode}"
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
        raise HTTPException(status_code=404,detail="Unknown service")
    body = await request.body()
    target_url = f"{baseurl}/{path}"

    if service == "auth":
        headers = dict(request.headers)
        headers.pop("host", None)

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

    response = await request.app.state.http_client.request(method=request.method,url=target_url,headers=headers,
    params=request.query_params,content=body,)
    return Response(content=response.content,status_code=response.status_code,headers=dict(response.headers),)