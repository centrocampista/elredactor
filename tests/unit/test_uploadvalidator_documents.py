from unittest.mock import AsyncMock, MagicMock

import pytest

from app.api.v1.routers.documents import UploadValidator


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
