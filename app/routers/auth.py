from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse
from app.config import settings
from app.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import User
from app.auth import create_access_token, get_current_user
from app.schemas import Token
import httpx
from sqlalchemy.future import select

router = APIRouter()

YANDEX_OAUTH_AUTHORIZE_URL = "https://oauth.yandex.com/authorize"
YANDEX_OAUTH_TOKEN_URL = "https://oauth.yandex.com/token"
YANDEX_API_USERINFO_URL = "https://login.yandex.ru/info"


@router.get("/login")
async def yandex_login():
    redirect_uri = "http://localhost:8000/auth/callback"
    params = {
         "response_type": "code",
         "client_id": settings.YANDEX_CLIENT_ID,
         "redirect_uri": redirect_uri
    }
    # Формируем URL для авторизации на Яндексе
    url = httpx.URL(YANDEX_OAUTH_AUTHORIZE_URL, params=params)
    return RedirectResponse(url)


@router.get("/callback")
async def yandex_callback(code: str, db: AsyncSession = Depends(get_db)):
    redirect_uri = "http://localhost:8000/auth/callback"
    # Обмен кода на access_token
    data = {
         "grant_type": "authorization_code",
         "code": code,
         "client_id": settings.YANDEX_CLIENT_ID,
         "client_secret": settings.YANDEX_CLIENT_SECRET,
         "redirect_uri": redirect_uri
    }
    async with httpx.AsyncClient() as client:
         token_response = await client.post(YANDEX_OAUTH_TOKEN_URL, data=data)
    if token_response.status_code != 200:
         raise HTTPException(status_code=400, detail="Ошибка при получении токена от Яндекса")
    token_json = token_response.json()
    access_token = token_json.get("access_token")
    # Получаем информацию о пользователе из Яндекса
    headers = {"Authorization": f"OAuth {access_token}"}
    async with httpx.AsyncClient() as client:
         user_response = await client.get(YANDEX_API_USERINFO_URL, headers=headers)
    if user_response.status_code != 200:
         raise HTTPException(status_code=400, detail="Не удалось получить информацию о пользователе от Яндекса")
    user_data = user_response.json()
    yandex_id = user_data.get("id")
    email = user_data.get("default_email")
    full_name = user_data.get("real_name", "")

    if not yandex_id or not email:
         raise HTTPException(status_code=400, detail="Неверные данные пользователя от Яндекса")

    # Если пользователь уже существует, получаем его; иначе – создаём
    query = select(User).where(User.yandex_id == yandex_id)
    result = await db.execute(query)
    user = result.scalars().first()
    if not user:
         user = User(email=email, full_name=full_name, yandex_id=yandex_id)
         db.add(user)
         await db.commit()
         await db.refresh(user)
    # Генерируем внутренний токен
    internal_token = create_access_token({"sub": str(user.id)})
    user.internal_token = internal_token
    db.add(user)
    await db.commit()
    return {"access_token": internal_token, "token_type": "bearer"}


@router.post("/refresh", response_model=Token)
async def refresh_token(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    new_token = create_access_token({"sub": str(current_user.id)})
    current_user.internal_token = new_token
    db.add(current_user)
    await db.commit()
    return {"access_token": new_token, "token_type": "bearer"}
