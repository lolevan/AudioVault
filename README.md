# Audio Upload Service

Сервис позволяет пользователям загружать аудио-файлы, проходить авторизацию через Яндекс OAuth и управлять своими данными. В реализации используется FastAPI, SQLAlchemy, асинхронный код и PostgreSQL 16. Файлы сохраняются локально, без использования облачного хранилища.

## Возможности

- **Авторизация через Яндекс OAuth**  
  Пользователь проходит авторизацию через Яндекс, после чего ему выдаётся внутренний JWT‑токен для доступа к API.
- **Эндпоинты:**
  - **Авторизация:**
    - `GET /auth/login` – перенаправление на страницу авторизации Яндекса.
    - `GET /auth/callback` – обработка callback от Яндекса, получение информации о пользователе и выдача JWT‑токена.
    - `POST /auth/refresh` – обновление внутреннего access_token.
  - **Управление пользователями:**
    - `GET /users/me` – получение данных текущего пользователя.
    - `PUT /users/me` – обновление данных пользователя.
    - `DELETE /users/{user_id}` – удаление пользователя (только для суперпользователя).
  - **Работа с аудио-файлами:**
    - `POST /files/upload` – загрузка аудио-файла с указанием его имени.
    - `GET /files/` – получение списка загруженных аудио-файлов (имя файла и путь к локальному хранилищу).

## Структура проекта

```
project/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── auth.py
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── users.py
│   │   └── files.py
│   └── services/
│       ├── __init__.py
│       ├── user_service.py
│       └── file_service.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Настройка переменных окружения

Для безопасного хранения ключей и настроек используется файл `.env`. Создайте в корне проекта файл `.env` со следующим содержимым:

```env
YANDEX_CLIENT_ID=your_actual_yandex_client_id
YANDEX_CLIENT_SECRET=your_actual_yandex_client_secret
SECRET_KEY=your_actual_secret_key
ACCESS_TOKEN_EXPIRE_MINUTES=30
DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/postgres
```

> **Важно:** Файл `.env` должен быть добавлен в `.gitignore`, чтобы секреты не попадали в публичный репозиторий.

## Установка и запуск

### Требования

- Docker и Docker Compose

### Шаги для запуска:

1. **Клонируйте репозиторий:**

   ```bash
   git clone https://github.com/lolevan/AudioVault.git
   cd AudioVault
   ```

2. Отредактируйте файл `.env` и укажите свои реальные значения для:
   - `YANDEX_CLIENT_ID`
   - `YANDEX_CLIENT_SECRET`
   - `SECRET_KEY`

3. **Соберите и запустите контейнеры с помощью Docker Compose:**

   ```bash
   docker-compose up --build
   ```

4. **Доступ к API:**

   Сервис будет доступен по адресу: [http://localhost:8000](http://localhost:8000)

5. **Документация по API:**

   Для просмотра интерактивной документации перейдите по адресу [http://localhost:8000/docs](http://localhost:8000/docs)

> **Примечание по OAuth в Swagger UI:**  
> Эндпоинт `/auth/login` реализован как GET для редиректа на Яндекс, поэтому при использовании Swagger UI (OAuth2PasswordBearer) автоматическое получение токена методом POST не сработает. Рекомендуется вручную пройти авторизацию через браузер, получить JWT‑токен, затем нажать кнопку «Authorize» в Swagger UI и вставить полученный токен.

## Примеры тестирования эндпоинтов с помощью curl

### 1. Проверка работы сервера (Root endpoint)

```bash
curl http://localhost:8000/
```

_Ожидаемый ответ:_

```json
{"message": "Сервис загрузки аудио-файлов запущен."}
```

---

### 2. Авторизация через Яндекс

#### a) Запуск авторизации

Откройте в браузере:

```
http://localhost:8000/auth/login
```

Это перенаправит вас на страницу авторизации Яндекса. После успешного входа Яндекс перенаправит на ваш callback URL (например, `http://localhost:8000/auth/callback?code=ВАШ_CODE&cid=...`).

#### b) Обработка callback

После авторизации Яндекса вы попадёте на URL вида:

```
http://localhost:8000/auth/callback?code=ВАШ_CODE&cid=...
```

_Этот эндпоинт обрабатывает полученный код и возвращает JWT‑токен._

---

### 3. Обновление JWT‑токена

```bash
curl -X POST http://localhost:8000/auth/refresh \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

_Замените `YOUR_JWT_TOKEN` на действительный токен._

---

### 4. Получение информации о текущем пользователе

```bash
curl -X GET http://localhost:8000/users/me \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

_Ожидаемый ответ: JSON с данными пользователя._

---

### 5. Обновление данных пользователя

Пример обновления имени пользователя:

```bash
curl -X PUT http://localhost:8000/users/me \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"full_name": "Новое Имя"}'
```

---

### 6. Удаление пользователя (только для суперпользователя)

```bash
curl -X DELETE http://localhost:8000/users/USER_ID \
  -H "Authorization: Bearer YOUR_SUPERUSER_JWT_TOKEN"
```

_Замените `USER_ID` на ID пользователя, а `YOUR_SUPERUSER_JWT_TOKEN` на токен суперпользователя._

---

### 7. Загрузка аудио-файла

Используйте multipart/form-data для загрузки файла:

```bash
curl -X POST http://localhost:8000/files/upload \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "file=@/path/to/your/file.mp3" \
  -F "file_name=Имя файла"
```

_Замените `/path/to/your/file.mp3` на путь к вашему файлу._

---

### 8. Получение списка аудио-файлов

```bash
curl -X GET http://localhost:8000/files/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

_Ожидаемый ответ: JSON со списком файлов, загруженных пользователем._

---

## Дополнительные Примечания

- **Безопасность:**  
  Все секретные ключи и настройки хранятся в файле `.env`, который не должен попадать в репозиторий.
  
- **Асинхронность:**  
  В проекте используется асинхронный доступ к базе данных (SQLAlchemy с asyncpg) и асинхронное сохранение файлов (aiofiles).

- **OAuth через Яндекс:**  
  Для корректного функционирования OAuth убедитесь, что в настройках вашего приложения в Яндекс указаны правильные `redirect_uri` (например, `http://localhost:8000/auth/callback`).

- **Swagger UI:**  
  Интерактивная документация доступна по адресу [http://localhost:8000/docs](http://localhost:8000/docs). При использовании авторизации в Swagger UI получите JWT‑токен через браузер и введите его вручную, поскольку автоматическое получение токена методом POST не работает для эндпоинта `/auth/login`.

## Развертывание в Production

При переходе в production‑среду рекомендуется:
- Использовать HTTPS для обеспечения безопасности соединений.
- Хранить секреты в защищённых хранилищах (например, Vault, переменные окружения на сервере и т.д.).
- Настроить надёжный логинг и мониторинг.
