import logging
from urllib.parse import quote
from fastapi import APIRouter, Depends, UploadFile, File
from fastapi.responses import JSONResponse, Response

from src.media import dependencies
from src.media.domain.schemas import UploadMediaRequest
from src.media.usecase import UploadMedia, GetMedia, MediaNotFoundError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/media", tags=["Media"])


@router.post("", status_code=201)
async def upload_media(
    file: UploadFile = File(...),
    usecase: UploadMedia = Depends(dependencies.upload_media_uc),
):
    if not file or not file.filename:
        return JSONResponse(
            status_code=400,
            content={"error": "Missing file or malformed multipart request"},
        )

    file_bytes = await file.read()
    
    req = UploadMediaRequest(
        filename=file.filename,
        content_type=file.content_type or "application/octet-stream",
        size=len(file_bytes),
        data=file_bytes,
    )

    media_id = await usecase.execute(req)
    return JSONResponse(status_code=201, content={"id": media_id})


@router.get("/{media_id}")
async def get_media_by_id(
    media_id: str,
    usecase: GetMedia = Depends(dependencies.get_media_uc),
):
    try:
        file_bytes, content_type, filename = await usecase.execute(media_id)
        return Response(
            content=file_bytes,
            media_type=content_type,
            headers={
                "Content-Disposition": f"inline; filename*=UTF-8''{quote(filename, safe='')}"
            }
        )
    except MediaNotFoundError:
        return JSONResponse(
            status_code=404,
            content={"error": "Media file not found"},
        )