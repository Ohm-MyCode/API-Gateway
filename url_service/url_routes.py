from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Request
from fastapi.responses import RedirectResponse
from nanoid import generate
from redis import RedisError
from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from url_service.config import settings
from url_service.database import SessionLocal
from url_service.logger import log
from url_service.metrics import (
    cache_metrics,
    shortcode_not_found,
    total_redirects,
    total_shortcodes_created,
)
from url_service.models import Url
from url_service.schema import GetUrlModel, ReturnUrlModel

router = APIRouter()

async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        await db.close()

async def get_current_user_id(request: Request) -> int:
    user_id = request.headers.get("x-user-id")
    if not user_id:
        raise HTTPException(status_code = 401 , detail = "Please Login Again")
    return int(request.headers["x-user-id"])


@router.post("/shorten")
async def create_new_shortcode(body:GetUrlModel,db:Annotated[AsyncSession, Depends(get_db)],
                               uid:Annotated[int, Depends(get_current_user_id)]):
    while(True):
        try:
            shortcode=generate(size=8)
            new_url = Url(owner_id=uid,original_url=body.url,shortcode=shortcode)
            db.add(new_url)
            await db.commit()
            total_shortcodes_created.inc()
            return{'Message':'ShortCode created Successfully'}
        except IntegrityError:
            log.info("Generated Shortcode clashed")
            continue

@router.delete("/delete/{short_code}")
async def delete_shortcode(request:Request, short_code:Annotated[str,Path(min_length=8, max_length=8)],db:Annotated[AsyncSession, Depends(get_db)],
                           uid:Annotated[int, Depends(get_current_user_id)]):
    stmt = select(Url).where(Url.shortcode==short_code)
    result = await db.scalar(stmt)
    if (result is None) or (result.owner_id != uid):
        raise HTTPException(status_code=409, detail="ShortCode not found")
    stmt = delete(Url).where(Url.shortcode ==short_code)
    await db.execute(stmt)
    await db.commit()

    redis = request.app.state.redis_client
    try:
        await redis.delete(f"url:{short_code}")
    except RedisError:
        log.error("Redis Unreachable")
    return {'Message':'ShortCode and Url deleted successfully'}

@router.get("/get_url/{short_code}",response_model=ReturnUrlModel)
async def get_short_code(short_code:Annotated[str,Path(min_length=8, max_length=8)],db:Annotated[AsyncSession, Depends(get_db)],
                 uid:Annotated[int, Depends(get_current_user_id)]):
    stmt = select(Url).where(Url.shortcode==short_code)
    result = await db.scalar(stmt)
    if (result is None) or (result.owner_id != uid):
        raise HTTPException(status_code=404, detail="ShortCode not found")
    return result

@router.get("/get_urls",response_model=list[ReturnUrlModel])
async def get_all_shortcodes(db:Annotated[AsyncSession, Depends(get_db)],uid:Annotated[int, Depends(get_current_user_id)]):
    stmt = select(Url).where(Url.owner_id==uid)
    result = await db.scalars(stmt)
    if result is None:
        raise HTTPException(status_code=404, detail="ShortCode not found")
    return result

@router.patch("/update/{short_code}")
async def update_shortcode(short_code:Annotated[str,Path(min_length=8, max_length=8)],db:Annotated[AsyncSession, Depends(get_db)],
                           uid:Annotated[int, Depends(get_current_user_id)],body:GetUrlModel,request:Request):
    stmt = select(Url).where(Url.shortcode==short_code)
    result = await db.scalar(stmt)
    if (result is None) or (result.owner_id != uid):
        raise HTTPException(status_code=409, detail="ShortCode not found")
    result.original_url = body.url
    await db.commit()
    redis = request.app.state.redis_client
    try:
        await redis.delete(f"url:{short_code}")
    except RedisError:
        log.error("Redis Unreachable")
    return{'Message':'Updated Successfully'}




async def lookup_and_cache(short_code: str, db: AsyncSession, redis) -> str:
    stmt = select(Url).where(Url.shortcode == short_code)
    result = (await db.scalar(stmt))

    if result is None:
        shortcode_not_found.inc()
        raise HTTPException(status_code=404, detail="Link Not Found/Deleted")

    try:
        await redis.set(f"url:{short_code}", result.original_url, ex=settings.ttl)
    except RedisError:
        log.error("redis_unreachable", operation="shortcode_cache_write")

    cache_metrics.labels(result="Cache Miss").inc()
    total_redirects.inc()
    return result.original_url


@router.get("/{short_code}")
async def get_url(short_code:Annotated[str,Path(min_length=8, max_length=8)], db: Annotated[AsyncSession, 
                    Depends(get_db)], request: Request):
    
    redis = request.app.state.redis_client

    try:
        destination_url = await redis.get(f"url:{short_code}")
    except RedisError:
        log.error("redis_unreachable", operation="shortcode_cache_read")
        destination_url = None

    if destination_url is not None:
        cache_metrics.labels(result="Cache Hit").inc()
        total_redirects.inc()
        return RedirectResponse(destination_url)

    destination_url = await lookup_and_cache(short_code, db, redis)
    return RedirectResponse(destination_url)