from time import perf_counter

from nanoid import generate

from gateway.logger import log
from gateway.metrics import request_latency


async def req_logging(request,call_next):
    request_id = str(generate())
    request.state.request_id = request_id
    start = perf_counter()
    
    try:
        response = await call_next(request)
    except Exception:
            log.exception(
                "request_failed",
                request_id=request_id,
                method=request.method,
                path=request.url.path,
                duration_ms=round(
                    (perf_counter() - start) * 1000, 2
                ),
            )
            request_latency.observe(round((perf_counter() - start) * 1000, 2))
            raise
    

    log.info(
            "request_completed",
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=round(
                (perf_counter() - start) * 1000, 2
            ),
        )
    request_latency.observe(round((perf_counter() - start) * 1000, 2))

    return response