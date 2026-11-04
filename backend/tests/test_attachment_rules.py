from io import BytesIO

import pytest
from fastapi import UploadFile

from app.errors import BadRequestError
from app.models import ContentType
from app.services.attachment_service import detect_type, read_limited


def make_upload(content: bytes) -> UploadFile:
    return UploadFile(file=BytesIO(content), filename="file.bin")


@pytest.mark.parametrize(
    "prefix, expected_type, expected_extension",
    [
        (b"\x89PNG", ContentType.PNG, ".png"),
        (b"\xff\xd8\xff", ContentType.JPEG, ".jpg"),
        (b"%PDF-", ContentType.PDF, ".pdf"),
    ],
)
def test_known_types_are_detected(prefix: bytes, expected_type: ContentType, expected_extension: str) -> None:
    content_type, extension = detect_type(prefix + b"rest of the file")
    assert content_type == expected_type
    assert extension == expected_extension


@pytest.mark.parametrize(
    "content",
    [
        b"hello world",
        b"",
        b"<html><script>alert(1)</script></html>",
        b"text before \x89PNG",
        b"\x89PN",
        b"%PDF",
    ],
    ids=[
        "plain_text",
        "empty",
        "html_with_script",
        "png_marker_not_at_start",
        "truncated_png_marker",
        "pdf_marker_without_dash",
    ],
)
def test_unknown_content_is_rejected(content: bytes) -> None:
    with pytest.raises(BadRequestError):
        detect_type(content)


def test_small_file_is_read_completely() -> None:
    content = b"a small file"
    assert read_limited(make_upload(content), 100) == content


def test_file_over_the_limit_is_rejected() -> None:
    with pytest.raises(BadRequestError):
        read_limited(make_upload(b"x" * 11), 10)


def test_file_exactly_at_the_limit_is_accepted() -> None:
    content = b"x" * 10
    assert read_limited(make_upload(content), 10) == content