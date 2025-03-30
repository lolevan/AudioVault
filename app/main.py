from fastapi import FastAPI
from app.database import engine, Base
from app.routers import auth, users, files

app = FastAPI(title="Audio Upload Service")


# При запуске создаём таблицы в БД
@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Подключаем роутеры
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(files.router, prefix="/files", tags=["files"])


@app.get("/")
async def root():
    return {"message": "Сервис загрузки аудио-файлов запущен."}
