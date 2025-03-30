from app.models import User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select


async def get_user_by_yandex_id(db: AsyncSession, yandex_id: str):
    query = select(User).where(User.yandex_id == yandex_id)
    result = await db.execute(query)
    return result.scalars().first()


async def create_user(db: AsyncSession, email: str, full_name: str, yandex_id: str):
    user = User(email=email, full_name=full_name, yandex_id=yandex_id)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user
