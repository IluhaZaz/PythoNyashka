from sqlalchemy.ext.asyncio import AsyncSession
from src.media.infrastructure.storage.postgresql.models import MediaFile


class MediaRepository:
    def __init__(self, session: AsyncSession):
        self.session: AsyncSession = session

    async def create(
        self,
        media_id: str,
        filename: str,
        content_type: str,
        size: int,
        storage_path: str,
    ) -> str:
        media_file = MediaFile(
            id=media_id,
            filename=filename,
            content_type=content_type,
            size=size,
            storage_path=storage_path,
        )
        self.session.add(media_file)
        await self.session.flush()
        await self.session.commit()
        return media_file.id

    async def get_by_id(self, media_id: str) -> MediaFile | None:
        return await self.session.get(MediaFile, media_id)