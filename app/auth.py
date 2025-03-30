from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.config import settings
from app.schemas import TokenData
from app.database import get_db
from app.models import User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    credentials_exception = HTTPException(
         status_code=status.HTTP_401_UNAUTHORIZED,
         detail="Не удалось пройти аутентификацию",
         headers={"WWW-Authenticate": "Bearer"},
    )
    try:
         payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
         user_id: str = payload.get("sub")
         if user_id is None:
             raise credentials_exception
         token_data = TokenData(user_id=user_id)
    except JWTError:
         raise credentials_exception
    query = select(User).where(User.id == token_data.user_id)
    result = await db.execute(query)
    user = result.scalars().first()
    if user is None:
         raise credentials_exception
    return user


async def get_current_superuser(current_user: User = Depends(get_current_user)):
    if not current_user.is_superuser:
         raise HTTPException(status_code=400, detail="Недостаточно прав")
    return current_user
