from email import policy
from email.parser import BytesParser

import httpx


def assert_media_upload(
    request: httpx.Request,
    filename: str,
    data: bytes,
    content_type: str,
) -> None:
    mime_headers = (
        f"MIME-Version: 1.0\r\nContent-Type: {request.headers['content-type']}\r\n\r\n"
    ).encode("ascii")
    message = BytesParser(policy=policy.default).parsebytes(mime_headers + request.content)
    (part,) = message.iter_parts()
    assert part.get_param("name", header="content-disposition") == "file"
    assert part.get_filename() == filename
    assert part.get_content_type() == content_type
    assert part.get_payload(decode=True) == data
