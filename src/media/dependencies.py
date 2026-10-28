from collections.abc import AsyncIterator
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.media import usecase
from src.media.infrastructure.storage.postgresql.repository import MediaRepository
from src.media.infrastructure.storage.s3.client import S3Client, S3Config
from src.infrastructure.storage.postgresql.core import DBSession


async def get_session() -> AsyncIterator[AsyncSession]:
    async with DBSession() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise


def get_repository(
    session: AsyncSession = Depends(get_session),
) -> MediaRepository:
    return MediaRepository(session)


def get_s3_client() -> S3Client:
    return S3Client(S3Config())


def upload_media_uc(
    repo: MediaRepository = Depends(get_repository),
    s3_client: S3Client = Depends(get_s3_client),
) -> usecase.UploadMedia:
    return usecase.UploadMedia(repository=repo, s3_client=s3_client)


def get_media_uc(
    repo: MediaRepository = Depends(get_repository),
    s3_client: S3Client = Depends(get_s3_client),
) -> usecase.GetMedia:
    return usecase.GetMedia(repository=repo, s3_client=s3_client)