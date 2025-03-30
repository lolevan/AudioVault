from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from app.auth import get_current_user
from app.schemas import AudioFileOut
from app.models import AudioFile
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
import os
import uuid
import aiofiles
from sqlalchemy.future import select

router = APIRouter()

UPLOAD_DIR = "uploaded_files"

if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)


@router.post("/upload", response_model=AudioFileOut)
async def upload_audio(
    file: UploadFile = File(...),
    file_name: str = Form(...),
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Сохраняем файл локально
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_location = os.path.join(UPLOAD_DIR, unique_filename)
    async with aiofiles.open(file_location, 'wb') as out_file:
         content = await file.read()
         await out_file.write(content)
    audio_file = AudioFile(file_name=file_name, file_path=file_location, owner_id=current_user.id)
    db.add(audio_file)
    await db.commit()
    await db.refresh(audio_file)
    return audio_file


@router.get("/", response_model=list[AudioFileOut])
async def list_audio_files(current_user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    query = select(AudioFile).where(AudioFile.owner_id == current_user.id)
    result = await db.execute(query)
    files = result.scalars().all()
    return files
