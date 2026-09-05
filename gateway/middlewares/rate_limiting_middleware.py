import time

from fastapi.responses import JSONResponse
from redis.exceptions import RedisError

from gateway.config import AUTH_ROUTES, SERVICES, settings
from gateway.logger import log
from gateway.metrics import rate_limit_blocks


async def rate_limiter(request,call_next):
    if request.method == "GET":
            parts = request.url.path.strip("/").split("/")
            if len(parts) == 1 and parts[0] not in SERVICES:
                return await call_next(request)
    user_id= getattr(request.state,"userid",None)
    script = request.app.state.token_bucket_script
    current_time = int(time.time() * 1000)
    
    if user_id is not None:
        bucket_key=f"rl:user:{user_id}"
    else:
        ip = request.client.host if request.client else "unknown"
        bucket_key=f"rl:ip:{ip}"


    try:
        if user_id is not None:
            allowed = await script(keys=[bucket_key],args=[settings.max_capacity_url_routes,
                                                           settings.refill_rate,current_time,],)
        else:
            allowed = await script(keys=[bucket_key],args=[settings.max_capacity_auth_routes,
                                                        settings.refill_rate,current_time,],)
    except RedisError:
        log.critical("redis_error", operation="token_bucket_limiter",)
        if request.url.path in AUTH_ROUTES: #fail close for authroutes and fail open for others
            return JSONResponse(content ={"detail":"service unavailable"}, status_code=503)
        else:
            return await call_next(request)


    if allowed == 1:
        return await call_next(request)
    else:
        log.warning("rate_limiter_blocked",
                    rate_limit_type="user" if user_id is not None else "ip",
                    status_code=429,
                    path=request.url.path,
                )
        rate_limit_blocks.inc()
        
        return JSONResponse(status_code = 429, content = {"detail":"Too many attempts please try after sometime"})