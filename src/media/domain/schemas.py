from pydantic import BaseModel


class UploadMediaRequest(BaseModel):
    filename: str
    content_type: str
    size: int
    data: bytes