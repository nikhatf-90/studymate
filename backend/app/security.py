from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from .config import settings
from .database import get_db
from .models import User
pwd=CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto"); oauth=OAuth2PasswordBearer(tokenUrl="/api/auth/login")
def hash_password(value:str)->str: return pwd.hash(value)
def verify_password(value:str, hashed:str)->bool: return pwd.verify(value,hashed)
def token_for(user:User)->str: return jwt.encode({"sub":str(user.id),"exp":datetime.now(timezone.utc)+timedelta(minutes=settings.access_token_minutes)},settings.jwt_secret,algorithm=settings.jwt_algorithm)
def current_user(token:str=Depends(oauth),db:Session=Depends(get_db))->User:
    try: uid=int(jwt.decode(token,settings.jwt_secret,algorithms=[settings.jwt_algorithm])["sub"])
    except (JWTError,KeyError,ValueError): raise HTTPException(401,"Invalid or expired session",headers={"WWW-Authenticate":"Bearer"})
    user=db.get(User,uid)
    if not user: raise HTTPException(401,"Account not found")
    return user
