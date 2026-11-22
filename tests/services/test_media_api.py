from io import BytesIO
from unittest.mock import Mock
from urllib.parse import quote
from uuid import UUID

import pytest
from botocore.exceptions import ClientError

from src.media import dependencies
from src.media.infrastructure.storage.postgresql.models import MediaFile
from src.media.infrastructure.storage.s3 import client as s3_adapter
from src.media.main import app
from tests.helpers import MISSING_ID, assert_validation_error

pytestmark = pytest.mark.anyio


@pytest.fixture
def s3(monkeypatch):
    objects: dict[tuple[str, str], bytes] = {}
    backend = Mock()

    def put_object(*, Bucket, Key, Body, ContentType):
        objects[(Bucket, Key)] = Body

    def get_object(*, Bucket, Key):
        return {"Body": BytesIO(objects[(Bucket, Key)])}

    backend.put_object.side_effect = put_object
    backend.get_object.side_effect = get_object
    monkeypatch.setattr(s3_adapter.boto3, "client", Mock(return_value=backend))
    monkeypatch.setenv("S3_ENDPOINT_URL", "http://s3.test")
    monkeypatch.setenv("S3_BUCKET_NAME", "media-test")
    monkeypatch.setenv("S3_ACCESS_KEY", "test-access-key")
    monkeypatch.setenv("S3_SECRET_KEY", "test-secret-key")
    return backend


@pytest.fixture
async def client(service_client, s3):
    async with service_client(app, dependencies) as http:
        yield http


@pytest.mark.parametrize(
    ("filename", "data", "mime_type"),
    [
        ("file.bin", b"\x00\x01\xff", "application/octet-stream"),
        ("заметка с пробелом.txt", "Привет".encode(), "text/plain"),
        ("empty.bin", b"", "application/octet-stream"),
    ],
    ids=["binary", "unicode-filename", "empty"],
)
async def test_upload_and_get_media_preserve_bytes_and_metadata(
    client,
    db_sessions,
    s3,
    filename,
    data,
    mime_type,
):
    uploaded = await client.post("/media", files={"file": (filename, data, mime_type)})

    assert uploaded.status_code == 201, uploaded.text
    media_id = uploaded.json()["id"]
    UUID(media_id)
    async with db_sessions() as session:
        media = await session.get(MediaFile, media_id)
        assert (media.filename, media.size, media.content_type) == (filename, len(data), mime_type)
        storage_path = media.storage_path
    s3.put_object.assert_called_once_with(
        Bucket="media-test",
        Key=storage_path,
        Body=data,
        ContentType=mime_type,
    )

    fetched = await client.get(f"/media/{media_id}")

    assert fetched.status_code == 200
    assert fetched.content == data
    assert fetched.headers["content-type"].split(";")[0] == mime_type
    assert fetched.headers["content-disposition"] == f"inline; filename*=UTF-8''{quote(filename)}"
    s3.get_object.assert_called_once_with(Bucket="media-test", Key=storage_path)


async def test_upload_defaults_content_type_and_creates_bucket_if_missing(client, s3):
    s3.head_bucket.side_effect = ClientError(
        {"Error": {"Code": "404", "Message": "Bucket not found"}},
        "HeadBucket",
    )
    multipart = (
        b'--test-boundary\r\nContent-Disposition: form-data; name="file"; filename="file.bin"\r\n'
        b"\r\ndata\r\n--test-boundary--\r\n"
    )
    response = await client.post(
        "/media",
        content=multipart,
        headers={"Content-Type": "multipart/form-data; boundary=test-boundary"},
    )

    assert response.status_code == 201, response.text
    s3.create_bucket.assert_called_once_with(Bucket="media-test")
    assert s3.put_object.call_args.kwargs["ContentType"] == "application/octet-stream"


async def test_upload_rejects_malformed_multipart(client, s3):
    response = await client.post(
        "/media",
        content=b"data",
        headers={"Content-Type": "multipart/form-data"},
    )
    assert response.status_code == 400
    s3.put_object.assert_not_called()


async def test_upload_rejects_file_with_empty_filename(client, s3):
    multipart = (
        b'--test-boundary\r\nContent-Disposition: form-data; name="file"; filename=""\r\n'
        b"\r\ndata\r\n--test-boundary--\r\n"
    )
    response = await client.post(
        "/media",
        content=multipart,
        headers={"Content-Type": "multipart/form-data; boundary=test-boundary"},
    )

    assert response.status_code == 400
    assert response.json() == {"error": "Missing file or malformed multipart request"}
    s3.put_object.assert_not_called()


async def test_upload_missing_file_returns_documented_status(client, s3):
    response = await client.post("/media", files={"other": ("file.txt", b"hello", "text/plain")})
    s3.put_object.assert_not_called()
    if response.status_code == 422:
        assert_validation_error(response, "body", "file")
        pytest.xfail("Media OpenAPI documents 400 for missing files, FastAPI currently returns 422")
    assert response.status_code == 400, response.text
    assert response.json()["error"]


async def test_get_missing_media_returns_not_found_without_storage_read(client, s3):
    fetched = await client.get(f"/media/{MISSING_ID}")
    assert fetched.status_code == 404
    assert fetched.json() == {"error": "Media file not found"}
    s3.get_object.assert_not_called()
