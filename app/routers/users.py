from fastapi import APIRouter, Depends, HTTPException
from app.auth import get_current_user, get_current_superuser
from app.schemas import UserOut, UserUpdate
from app.models import User
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from sqlalchemy.future import select

router = APIRouter()


@router.get("/me", response_model=UserOut)
async def read_user_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.put("/me", response_model=UserOut)
async def update_user_me(user_update: UserUpdate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if user_update.full_name:
         current_user.full_name = user_update.full_name
    db.add(current_user)
    await db.commit()
    await db.refresh(current_user)
    return current_user


@router.delete("/{user_id}")
async def delete_user(user_id: str, superuser: User = Depends(get_current_superuser), db: AsyncSession = Depends(get_db)):
    query = select(User).where(User.id == user_id)
    result = await db.execute(query)
    user = result.scalars().first()
    if not user:
         raise HTTPException(status_code=404, detail="Пользователь не найден")
    await db.delete(user)
    await db.commit()
    return {"detail": "Пользователь удалён"}
