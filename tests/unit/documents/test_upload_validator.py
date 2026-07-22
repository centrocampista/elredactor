from unittest.mock import AsyncMock, MagicMock, patch

from fastapi import HTTPException
import pytest

from app.api.v1.routers.documents import UploadValidator

FAKE_MAX_FILE_SIZE = 100


@pytest.mark.parametrize(
    "content_type, side_effect_value",
    [
        ("application/pdf", [b"x" * FAKE_MAX_FILE_SIZE, b""]),
    ],
)
@pytest.mark.unit
async def test_file_equal_max_file_size(content_type, side_effect_value):
    file = MagicMock()
    file.content_type = content_type
    file.read = AsyncMock(side_effect=side_effect_value)

    with patch("app.api.v1.routers.documents.MAX_FILE_SIZE", FAKE_MAX_FILE_SIZE):
        validator = UploadValidator(file=file)
        result = await validator.validate()
    file_size, _ = side_effect_value
    assert result == file_size


@pytest.mark.parametrize(
    "content_type, side_effect_value",
    [
        ("application/pdf", [b"x" * FAKE_MAX_FILE_SIZE, b"x", b""]),
    ],
)
@pytest.mark.unit
async def test_file_over_max_file_size(content_type, side_effect_value):
    file = MagicMock()
    file.content_type = content_type
    file.read = AsyncMock(side_effect=side_effect_value)

    with patch("app.api.v1.routers.documents.MAX_FILE_SIZE", FAKE_MAX_FILE_SIZE):
        with pytest.raises(HTTPException) as http_except:
            validator = UploadValidator(file=file)
            await validator.validate()
    assert http_except.value.status_code == 413


@pytest.mark.parametrize(
    "content_type, return_value",
    [
        ("audio/mp3", b""),
    ],
)
@pytest.mark.unit
async def test_invalid_content_type(content_type, return_value):
    file = MagicMock()
    file.content_type = content_type
    file.read = AsyncMock(return_value=return_value)
    with pytest.raises(HTTPException) as http_except:
        validator = UploadValidator(file=file)
        await validator.validate()
    assert http_except.value.status_code == 415


@pytest.mark.parametrize(
    "content_type, return_value",
    [
        ("application/pdf", b""),
        ("text/plain", b""),
        ("text/markdown", b""),
        (
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            b"",
        ),
    ],
)
@pytest.mark.unit
async def test_valid_content_type(content_type, return_value):
    file = MagicMock()
    file.content_type = content_type
    file.read = AsyncMock(return_value=return_value)

    validator = UploadValidator(file=file)
    result = await validator.validate()

    assert result == return_value


@pytest.mark.parametrize(
    "content_type, side_effect_value",
    [
        ("application/pdf", [b"%PDF-1.4 content", b""]),
        ("text/plain", [b"plain text content", b""]),
        ("text/markdown", [b"# markdown content", b""]),
        (
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            [b"docx binary content", b""],
        ),
    ],
)
@pytest.mark.unit
async def test_returns_bytes(content_type, side_effect_value):
    file = MagicMock()
    file.content_type = content_type
    file.read = AsyncMock(side_effect=side_effect_value)
    content_value, _ = side_effect_value
    validator = UploadValidator(file=file)
    result = await validator.validate()

    assert result == content_value
