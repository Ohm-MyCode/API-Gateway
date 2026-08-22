from fastapi import APIRouter,Depends,HTTPException, status, Response,Cookie, Request
from auth_service.database import SessionLocal
from typing import Annotated
from .schema import UserLogin,CreateUser
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select,update,delete
from .models import User, RefreshToken
from fastapi.security import OAuth2PasswordBearer
from pwdlib import PasswordHash
import jwt,hmac,hashlib
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from datetime import datetime, timedelta, timezone
from .config import settings

#router = APIRouter(prefix="/auth")
router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="refresh")
password_hash = PasswordHash.recommended() 

async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        await db.close()


@router.post("/signup",status_code=status.HTTP_201_CREATED)
async def create_user(user:CreateUser, db:Annotated[AsyncSession,Depends(get_db)]):
    stmt= select(User).where(User.email==user.email)
    result = (await db.scalars(stmt)).first()
    if result is not None:
        raise HTTPException(status_code=409, detail="User Already Exists, Please Login")
    hashed = password_hash.hash(user.password)
    newuser= User(user_name=user.name, email=user.email, password_hash=hashed)
    db.add(newuser)
    await db.commit()
    return {"message":"User Created Successfully, Please login to use your account"}


@router.post("/login")
async def login(user:UserLogin, db:Annotated[AsyncSession,Depends(get_db)],response:Response):
    stmt = select(User).where(User.email==user.email)
    result = await db.scalar(stmt)
    if (result is None) or (not password_hash.verify(user.password, result.password_hash)):
        raise HTTPException(status_code=401, detail="Email/Password Combination is incorrect or doesn't exist.")
    expire_access = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    expire_refresh = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    access_token_payload ={"sub":str(result.id),"exp":expire_access,"type":"access"}
    refresh_token_payload ={"sub":str(result.id),"exp":expire_refresh,"type":"refresh"}
    access_token = jwt.encode(access_token_payload, settings.PRIVATE_KEY,algorithm=settings.JWT_ALGORITHM)
    refresh_token = jwt.encode(refresh_token_payload, settings.PRIVATE_KEY,algorithm=settings.JWT_ALGORITHM)
    hashed_reftoken= hmac.new(settings.TOKEN_HASH_KEY.encode(),refresh_token.encode(),hashlib.sha256).hexdigest()
    newtoken = RefreshToken(user_id = result.id, expires_at=expire_refresh,token_hash=hashed_reftoken)
    db.add(newtoken)
    await db.commit()
    await db.refresh(newtoken)
    response.set_cookie(key="refresh_token",value=refresh_token,httponly=True,secure=False,samesite="lax",path="/auth",  
    max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60)
    return {"access_token": access_token, "token_type": "bearer"}



@router.post("/refresh")
async def get_new_token(token:Annotated[str|None,Cookie(alias="refresh_token")],db:Annotated[AsyncSession,Depends(get_db)],response:Response):
    if token is None:
        raise HTTPException(status_code=401,detail = "Invalid Login. Please Login Again")
    try:
        incomming_tokenhash=hmac.new(settings.TOKEN_HASH_KEY.encode(),token.encode(),hashlib.sha256).hexdigest()
        _ = jwt.decode(token,settings.PUBLIC_KEY , algorithms=[settings.JWT_ALGORITHM])
        stmt=select(RefreshToken).where(RefreshToken.token_hash==incomming_tokenhash)
        result = (await db.scalars(stmt)).one_or_none()

        if (result is None):
            raise HTTPException(status_code=401,detail="Invalid Token. Login Again")

        if result.is_revoked == True:
                stmt = update(RefreshToken).where(RefreshToken.user_id == result.user_id).values(is_revoked=True)
                await db.execute(stmt)
                await db.commit()
                raise HTTPException(status_code=401, detail="Security alert — please log in again")
        
        expire_access = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        expire_refresh = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        refresh_token_payload ={"sub":str(result.user_id),"exp":expire_refresh,"type":"refresh"}
        access_token_payload ={"sub":str(result.user_id),"exp":expire_access,"type":"access"}
        access_token = jwt.encode(access_token_payload, settings.PRIVATE_KEY,settings.JWT_ALGORITHM)
        refresh_token = jwt.encode(refresh_token_payload, settings.PRIVATE_KEY,settings.JWT_ALGORITHM)
        hashed_reftoken= hmac.new(settings.TOKEN_HASH_KEY.encode(),refresh_token.encode(),hashlib.sha256).hexdigest()

        result.is_revoked=True
        newtoken = RefreshToken(user_id = result.user_id, expires_at=expire_refresh,token_hash=hashed_reftoken)
        db.add(newtoken)
        await db.commit()
        response.set_cookie(key="refresh_token",value=refresh_token,httponly=True,secure=False,samesite="lax",path="/auth",  
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60)
        return {"access_token": access_token, "token_type": "bearer"}
        
    except ExpiredSignatureError:
        raise HTTPException(status_code=401,detail="Session Expired,Login Again")

    except InvalidTokenError:
        raise HTTPException(status_code=401,detail="Session Expired,Login Again")

@router.post("/logout")
async def logout_current_device(token:Annotated[str|None,Cookie(alias="refresh_token")],db:Annotated[AsyncSession,Depends(get_db)],
                                response:Response):
    if token is None:
        response.delete_cookie(key="refresh_token", path="/auth")
        return {"detail": "Logged out"}
    incoming_hash = hmac.new(settings.TOKEN_HASH_KEY.encode(), token.encode(), hashlib.sha256).hexdigest()
    stmt = delete(RefreshToken).where(RefreshToken.token_hash == incoming_hash)
    await db.execute(stmt)
    await db.commit()

    response.delete_cookie(key="refresh_token", path="/auth")
    return {"detail": "Logged out"}

@router.post("/logout-all")
async def logout_all(token:Annotated[str|None,Cookie(alias="refresh_token")],db:Annotated[AsyncSession,Depends(get_db)],
                                response:Response):
    if token is None:
        raise HTTPException(status_code=401, detail="Invalid session")

    payload = jwt.decode(token, settings.PUBLIC_KEY, algorithms=[settings.JWT_ALGORITHM])
    user_id = int(payload["sub"])

    stmt = delete(RefreshToken).where(RefreshToken.user_id == user_id)
    await db.execute(stmt)
    await db.commit()

    response.delete_cookie(key="refresh_token", path="/auth")
    return {"detail": "Logged out of all devices"}