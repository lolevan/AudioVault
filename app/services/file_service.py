from app.models import AudioFile
from sqlalchemy.ext.asyncio import AsyncSession


async def create_audio_file(db: AsyncSession, file_name: str, file_path: str, owner_id):
    audio_file = AudioFile(file_name=file_name, file_path=file_path, owner_id=owner_id)
    db.add(audio_file)
    await db.commit()
    await db.refresh(audio_file)
    return audio_file
