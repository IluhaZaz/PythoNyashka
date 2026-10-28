import uuid
from src.media.infrastructure.storage.postgresql.repository import MediaRepository
from src.media.infrastructure.storage.s3.client import S3Client
from src.media.domain.schemas import UploadMediaRequest


class MediaNotFoundError(Exception):
    pass


class UploadMedia:
    def __init__(self, repository: MediaRepository, s3_client: S3Client):
        self.repository = repository
        self.s3_client = s3_client

    async def execute(self, req: UploadMediaRequest) -> str:
        media_id = str(uuid.uuid4())
        storage_path = f"files/{media_id}_{req.filename}"

        self.s3_client.upload_file(
            file_bytes=req.data,
            file_key=storage_path,
            content_type=req.content_type,
        )

        await self.repository.create(
            media_id=media_id,
            filename=req.filename,
            content_type=req.content_type,
            size=req.size,
            storage_path=storage_path,
        )

        return media_id


class GetMedia:
    def __init__(self, repository: MediaRepository, s3_client: S3Client):
        self.repository = repository
        self.s3_client = s3_client

    async def execute(self, media_id: str) -> tuple[bytes, str, str]:
        media_file = await self.repository.get_by_id(media_id)
        if media_file is None:
            raise MediaNotFoundError()

        file_bytes = self.s3_client.get_file(media_file.storage_path)

        return file_bytes, media_file.content_type, media_file.filename