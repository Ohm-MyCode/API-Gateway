from fastapi import APIRouter, Depends,HTTPException,Request,Path
from .database import SessionLocal
from fastapi.responses import RedirectResponse
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select,delete
from sqlalchemy.exc import IntegrityError
from .models import Url
from nanoid import generate
from .schema import GetUrlModel,ReturnUrlModel
router = APIRouter()

async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        await db.close()

async def get_current_user_id(request: Request) -> int:
    return int(request.headers["x-user-id"])


@router.post("/shorten")
async def create_new_shortcode(body:GetUrlModel,db:Annotated[AsyncSession, Depends(get_db)],
                               uid:Annotated[int, Depends(get_current_user_id)]):
    shortcode = generate(size=8)
    while(True):
        try:
            shortcode=generate(size=8)
            new_url = Url(owner_id=uid,original_url=body.url,shortcode=shortcode)
            db.add(new_url)
            await db.commit()
            return{'Message':'ShortCode created Successfully'}
        except IntegrityError:
            continue

@router.delete("/delete/{short_code}")
async def delete_shortcode(short_code:Annotated[str,Path(min_length=8, max_length=8)],db:Annotated[AsyncSession, Depends(get_db)],
                           uid:Annotated[int, Depends(get_current_user_id)]):
    stmt = select(Url).where(Url.shortcode==short_code)
    result = await db.scalar(stmt)
    if (result is None) or (result.owner_id != uid):
        raise HTTPException(status_code=409, detail="ShortCode not found")
    stmt = delete(Url).where(Url.shortcode ==short_code)
    await db.execute(stmt)
    await db.commit()
    return {'Message':'ShortCode and Url deleted successfully'}

@router.get("/url/{short_code}",response_model=ReturnUrlModel)
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
                           uid:Annotated[int, Depends(get_current_user_id)],body:GetUrlModel):
    stmt = select(Url).where(Url.shortcode==short_code)
    result = await db.scalar(stmt)
    if (result is None) or (result.owner_id != uid):
        raise HTTPException(status_code=409, detail="ShortCode not found")
    result.original_url = body.url
    await db.commit()
    return{'Message':'Updated Successfully'}

@router.get("/{shortcode}")
async def get_url(shortcode:str,db:Annotated[AsyncSession, Depends(get_db)]):
    stmt = select(Url).where(Url.shortcode==shortcode)
    result = (await db.scalars(stmt)).one_or_none()
    if result is None:
        raise HTTPException(status_code=404, detail="Link Not Found/Deleted")
    return RedirectResponse(result.original_url)