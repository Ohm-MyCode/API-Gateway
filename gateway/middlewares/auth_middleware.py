from gateway.config import SERVICES, AUTH_ROUTES, settings
from fastapi.responses import JSONResponse
import jwt
from gateway.logger import log

async def auth_middleware(request, call_next):

    if request.url.path in AUTH_ROUTES:
        return await call_next(request)

    if request.method == "GET":
        parts = request.url.path.strip("/").split("/")
        if len(parts) == 1 and parts[0] not in SERVICES:
            return await call_next(request)
        
    auth = request.headers.get("Authorization")
    if not auth:
        log.warning("authentication_failed",
                    path=request.url.path,
                        )
        return JSONResponse(
            {"detail": "Unauthorized"},
            status_code=401,
        )
    try:
        parts = auth.split()

        if len(parts) != 2 or parts[0].lower() != "bearer":
            return JSONResponse(
                {"detail": "Invalid auth header"},
                status_code=401,
            )

        token = parts[1]
        payload = jwt.decode(token,settings.PUBLIC_KEY , algorithms=[settings.JWT_ALGORITHM])
        request.state.userid = payload["sub"]
        
    except jwt.PyJWTError:
        log.warning("authentication_failed",path=request.url.path,)
        return JSONResponse({"details":"Unauthorized, try logging in again"},status_code=401)
    return await call_next(request)